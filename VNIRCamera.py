import stapipy as st
import cv2
import numpy as np

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

        return nparr