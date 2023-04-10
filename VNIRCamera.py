import stapipy as st
import cv2
import numpy as np

class Band():
    int ColAvg
    int RowAvg
    int Col
    int Row
    int ColInc
    int RowInc


class VNIRCamera():
    def __init__(self):
        st.initialize()
        st_system = st.create_system()
        self.st_device = st_system.create_first_device()
        print('Device=', self.st_device.info.display_name)
    
    def get_image(self):
        DISPLAY_RESIZE_FACTOR = 0.3
        st_datastream = self.st_device.create_datastream()
        st_datastream.start_acquisition(1)

        # Start the image acquisition of the camera side.
        self.st_device.acquisition_start()

        # A while loop for acquiring data and checking status
        while st_datastream.is_grabbing:
            # Create a localized variable st_buffer using 'with'
            # Warning: if st_buffer is in a global scope, st_buffer must be
            #          assign to None to allow Garbage Collector release the buffer
            #          properly.
            with st_datastream.retrieve_buffer() as st_buffer:
                # Check if the acquired data contains image data.
                if st_buffer.info.is_image_present:
                    # Create an image object.
                    st_image = st_buffer.get_image()

                    # Display the information of the acquired image data.
                    print("BlockID={0} Size={1} x {2} First Byte={3}".format(
                        st_buffer.info.frame_id,
                        st_image.width, st_image.height,
                        st_image.get_image_data()[0]))

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

                    # Perform color conversion for Bayer.
                    if pixel_format_info.is_bayer:
                        bayer_type = pixel_format_info.get_pixel_color_filter()
                        if bayer_type == st.EStPixelColorFilter.BayerRG:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_RG2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerGR:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GR2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerGB:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_GB2RGB)
                        elif bayer_type == st.EStPixelColorFilter.BayerBG:
                            nparr = cv2.cvtColor(nparr, cv2.COLOR_BAYER_BG2RGB)

                    # Resize image.and display.
                    nparr = cv2.resize(nparr, None,
                                    fx=DISPLAY_RESIZE_FACTOR,
                                    fy=DISPLAY_RESIZE_FACTOR)
                    cv2.imshow('image', nparr)
                    cv2.waitKey(1)
                else:
                    # If the acquired data contains no image data.
                    print("Image data does not exist.")

        # Stop the image acquisition of the camera side
        self.st_device.acquisition_stop()

        # Stop the image acquisition of the host side
        st_datastream.stop_acquisition()
        image_tuple = self.demosaic(nparr)
        return image_tuple

    def demosaic(self,image):
        col_avg = 1
        row_avg = 1
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
        int imageRows = 2048
        int imageCols = 2048
        int s = 2048*2048
        # demosaic the image - image will be smaller by a factor related to dr and dc
        int sum
        int n
        int r
        int tr
        int c
        int tc
        int kr
        int kc
        int kci
        int kri
        int avg
        int sindex

        r = red_row
        for tr in range(imageRows/row_inc):
            c = red_col
            for tc in range(imageCols/col_inc):
                sum = 0
                n = 0
                kr = r
                for kri in range(row_avg):
                    kc = c
                    for kci in range(col_avg):
                        sindex = imageCols * kr + kc
                        if (sindex > s)
                            break
                        sum+=image[kr,kc]
                        n += 1
                        kc += 1
                    kr += 1
                if n ~= 0:
                    avg = sum/n
                else:
                    avg = 0
                if avg > 255:
                    avg = 255
                red[tr,tc] = avg
                c += col_inc
            r += row_inc
        
        r = green_row
        for tr in range(imageRows/row_inc):
            c = green_col
            for tc in range(imageCols/col_inc):
                sum = 0
                n = 0
                kr = r
                for kri in range(row_avg):
                    kc = c
                    for kci in range(col_avg):
                        sindex = imageCols * kr + kc
                        if (sindex > s)
                            break
                        sum+=image[kr,kc]
                        n += 1
                        kc += 1
                    kr += 1
                if n ~= 0:
                    avg = sum/n
                else:
                    avg = 0
                if avg > 255:
                    avg = 255
                green[tr,tc] = avg
                c += col_inc
            r += row_inc

        r = blue_row
        for tr in range(imageRows/row_inc):
            c = blue_col
            for tc in range(imageCols/col_inc):
                sum = 0
                n = 0
                kr = r
                for kri in range(row_avg):
                    kc = c
                    for kci in range(col_avg):
                        sindex = imageCols * kr + kc
                        if (sindex > s)
                            break
                        sum+=image[kr,kc]
                        n += 1
                        kc += 1
                    kr += 1
                if n ~= 0:
                    avg = sum/n
                else:
                    avg = 0
                if avg > 255:
                    avg = 255
                blue[tr,tc] = avg
                c += col_inc
            r += row_inc
        
        r = nir_row
        for tr in range(imageRows/row_inc):
            c = nir_col
            for tc in range(imageCols/col_inc):
                sum = 0
                n = 0
                kr = r
                for kri in range(row_avg):
                    kc = c
                    for kci in range(col_avg):
                        sindex = imageCols * kr + kc
                        if (sindex > s)
                            break
                        sum+=image[kr,kc]
                        n += 1
                        kc += 1
                    kr += 1
                if n ~= 0:
                    avg = sum/n
                else:
                    avg = 0
                if avg > 255:
                    avg = 255
                nir[tr,tc] = avg
                c += col_inc
            r += row_inc
        return (red, green, blue, nir)