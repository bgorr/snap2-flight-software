import stapipy as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

class VNIRCamera():
    def __init__(self):
        initialized = False
        while not initialized:
            try:
                st.initialize()
                st_system = st.create_system()
                self.st_device = st_system.create_first_device()
                self.camera_count = 100
                self.st_datastream = self.st_device.create_datastream()
                initialized = True
            except:
                print("retrying camera init")
    def run_adaptive_exposure(self):
        print("Running adaptive exposure!")
        img_quality = False
        while(img_quality == False):
            remote_nodemap = self.st_device.remote_port.nodemap
            self.st_datastream.start_acquisition(1)

            # Start the image acquisition of the camera side.
            self.st_device.acquisition_start()

            # A while loop for acquiring data and checking status
            while self.st_datastream.is_grabbing:
                # Create a localized variable st_buffer using 'with'
                # Warning: if st_buffer is in a global scope, st_buffer must be
                #          assign to None to allow Garbage Collector release the buffer
                #          properly.
                with self.st_datastream.retrieve_buffer() as st_buffer:
                    # Check if the acquired data contains image data.
                    if st_buffer.info.is_image_present:
                        # Create an image object.
                        st_image = st_buffer.get_image()

                        # Check the pixelformat of the input image.
                        pixel_format = st_image.pixel_format
                        pixel_format_info = st.get_pixel_format_info(pixel_format)

                        # Only mono or bayer is processed.
                        if not(pixel_format_info.is_mono or pixel_format_info.is_bayer):
                            continue

                        # Get raw image data.
                        data = st_image.get_image_data()

                        # Perform pixel value scaling if each pixel component is
                        # larger than 8bit. Example: 10bit Bayer/Mono, 12bit, etc.
                        if pixel_format_info.each_component_total_bit_count > 8:
                            nparr = np.frombuffer(data, np.uint16)
                            division = pow(2, pixel_format_info
                                        .each_component_valid_bit_count - 8)
                            nparr = (nparr / division).astype('uint8')
                        else:
                            nparr = np.frombuffer(data, np.uint8)

                        # Process image for display.
                        nparr = nparr.reshape(st_image.height, st_image.width, 1)
                        image_tuple = self.demosaic(nparr)
                        nparr = image_tuple[0]
                    else:
                        # If the acquired data contains no image data.
                        print("Image data does not exist.")

            # Stop the image acquisition of the camera side
            self.st_device.acquisition_stop()

            # Stop the image acquisition of the host side
            self.st_datastream.stop_acquisition()
            EXPOSURE_MODE = "ExposureMode"
            EXPOSURE_TIME = "ExposureTime"
            EXPOSURE_TIME_RAW = "ExposureTimeRaw"
            AUTO_LIGHT_TARGET = "AutoLightTarget"
            expose_max = 100000
            expose_min = 10
            over,under = self.check_img(nparr)
            if over == True:
                print("overexposed = True")
            if under == True:
                print("underexposed = True")

            node = remote_nodemap.get_node(EXPOSURE_TIME_RAW)
            if node.principal_interface_type == st.EGCInterfaceType.IFloat:
                node_value = st.PyIFloat(node)
            elif node.principal_interface_type == st.EGCInterfaceType.IInteger:
                node_value = st.PyIInteger(node)
            if over == True:
                
                EXPOSURE_TIME_RAW_int = int(node_value.value)
                EXPOSURE_TIME_RAW_int = 0.5*(EXPOSURE_TIME_RAW_int-expose_min)
                print("New exposure time: ", EXPOSURE_TIME_RAW_int)
                self.edit_setting(remote_nodemap, EXPOSURE_TIME_RAW, EXPOSURE_TIME_RAW_int)

            elif under == True:
                EXPOSURE_TIME_RAW_int = int(node_value.value)
                EXPOSURE_TIME_RAW_int = 0.5*(EXPOSURE_TIME_RAW_int+expose_max)
                print("New exposure time: ", EXPOSURE_TIME_RAW_int)
                self.edit_setting(remote_nodemap, EXPOSURE_TIME_RAW, EXPOSURE_TIME_RAW_int)

            else: pass
            if under == False and over == False:
                img_quality = True

    def check_img(self,image):
        tol = 15
        over = False
        under = False
        ctrl_std = 75
        image = image[0:255,0:255]
        hist1,hist1_bins = np.histogram(image.flatten(),256,[0,255],density=True)
        hist1_mids = 0.5*(hist1_bins[1:]+hist1_bins[:-1])
        hist1_mean = np.average(hist1_mids,weights=hist1)
        hist1_std = np.sqrt(np.average((hist1_mids-hist1_mean)**2, weights=hist1))
        print(hist1_mean)
        print(hist1_std)
        check_std = np.abs(hist1_std-ctrl_std)

        if check_std >= tol:
            p = 0 
            while p < 256:
                if hist1[p] == np.max(hist1):
                    hist1_maxpixel = p
                    p += 1
                else:
                    pass
                    p += 1

            if hist1_maxpixel > 256/2 or hist1_mean > 235:
                over = True
            elif hist1_maxpixel <= 256/2 or hist1_mean < 20:
                under = True
        else: pass
        return (over,under)


    def edit_setting(self,nodemap, node_name, value):
        """
        Edit setting which has numeric type.

        :param nodemap:  Node map.
        :param node_name: Node name.
        """
        node = nodemap.get_node(node_name)
        if not node.is_writable:
            return
        if node.principal_interface_type == st.EGCInterfaceType.IFloat:
            node_value = st.PyIFloat(node)
        elif node.principal_interface_type == st.EGCInterfaceType.IInteger:
            node_value = st.PyIInteger(node)
        while True:
            # print(node_name)
            # print(" Min={0} Max={1} Current={2}{3}".format(
            #     node_value.min, node_value.max, node_value.value,
            #     " Inc={0}".format(node_value.inc) if\
            #             node_value.inc_mode == st.EGCIncMode.FixedIncrement\
            #             else ""))
            new_value = value
            #print()
            if node.principal_interface_type == st.EGCInterfaceType.IFloat:
                new_numeric_value = float(new_value)
            else:
                new_numeric_value = int(new_value)
            if node_value.min <= new_numeric_value <= node_value.max:
                node_value.value = new_numeric_value
                return
    
    def get_image(self):
        if self.camera_count > 100:
            self.run_adaptive_exposure()
            self.camera_count = 0

        self.st_datastream.start_acquisition(1)

        # Start the image acquisition of the camera side.
        self.st_device.acquisition_start()

        # A while loop for acquiring data and checking status
        while self.st_datastream.is_grabbing:
            # Create a localized variable st_buffer using 'with'
            # Warning: if st_buffer is in a global scope, st_buffer must be
            #          assign to None to allow Garbage Collector release the buffer
            #          properly.
            with self.st_datastream.retrieve_buffer() as st_buffer:
                # Check if the acquired data contains image data.
                if st_buffer.info.is_image_present:
                    # Create an image object.
                    st_image = st_buffer.get_image()

                    # Check the pixelformat of the input image.
                    pixel_format = st_image.pixel_format
                    pixel_format_info = st.get_pixel_format_info(pixel_format)

                    # Only mono or bayer is processed.
                    if not(pixel_format_info.is_mono or pixel_format_info.is_bayer):
                        continue

                    # Get raw image data.
                    data = st_image.get_image_data()

                    # Perform pixel value scaling if each pixel component is
                    # larger than 8bit. Example: 10bit Bayer/Mono, 12bit, etc.
                    if pixel_format_info.each_component_total_bit_count > 8:
                        nparr = np.frombuffer(data, np.uint16)
                        division = pow(2, pixel_format_info
                                    .each_component_valid_bit_count - 8)
                        nparr = (nparr / division).astype('uint8')
                    else:
                        nparr = np.frombuffer(data, np.uint8)

                    # Process image for display.
                    nparr = nparr.reshape(st_image.height, st_image.width, 1)
                else:
                    # If the acquired data contains no image data.
                    print("Image data does not exist.")

        # Stop the image acquisition of the camera side
        self.st_device.acquisition_stop()

        # Stop the image acquisition of the host side
        self.st_datastream.stop_acquisition()
        image_tuple = self.demosaic(nparr)
        self.camera_count += 1
        return image_tuple

    def demosaic(self,image):
        col_inc = 4
        row_inc = 4
        red_col = 0
        red_row = 0
        green_col = 0
        green_row = 2
        blue_col = 2
        blue_row = 0
        nir_col = 2
        nir_row = 2
        red = np.zeros(shape=(512,512))
        green = np.zeros(shape=(512,512))
        blue = np.zeros(shape=(512,512))
        nir = np.zeros(shape=(512,512))
        imageRows = 2048
        imageCols = 2048
        s = 2048*2048
        # demosaic the image - image will be smaller by a factor related to dr and dc
        r = red_row
        for tr in range(int(imageRows/row_inc)):
            c = red_col
            for tc in range(int(imageCols/col_inc)):
                red[tr,tc] = image[r,c]
                c += col_inc
            r += row_inc
        r = green_row
        for tr in range(int(imageRows/row_inc)):
            c = green_col
            for tc in range(int(imageCols/col_inc)):
                green[tr,tc] = image[r,c]
                c += col_inc
            r += row_inc
        r = blue_row
        for tr in range(int(imageRows/row_inc)):
            c = blue_col
            for tc in range(int(imageCols/col_inc)):
                blue[tr,tc] = image[r,c]
                c += col_inc
            r += row_inc
        r = nir_row
        for tr in range(int(imageRows/row_inc)):
            c = nir_col
            for tc in range(int(imageCols/col_inc)):
                nir[tr,tc] = image[r,c]
                c += col_inc
            r += row_inc
        return (red, green, blue, nir)