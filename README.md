# Steganography

This program allows you to encode text data in a PNG image and then decode it. The program's operation is based on the modification of image pixels based on the provided key and text data.

During encryption, the program selects pixels to be modified based on the hashed key and the given message. It then modifies the pixel values to encode the binary ASCII representation of the message, adding a control bit at the end.

During decryption, the program reads the pixel values from the image, recreates the binary ASCII representation of the data, and then decodes it back to text. It also reads the value of the control bit to determine whether the data has been encrypted correctly.

Additionally, if an incorrect key is entered during decoding, the program imposes a penalty by changing the pixel value, and if the number of decoding attempts is exceeded, it randomly shuffles the pixels, which leads to image destruction.
