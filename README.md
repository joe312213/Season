# Season
basic encryption lib. currently works with ascii data

This package started as a way to allow my students to use encryption with their projects, in a very locked down Python environment. It is also my first somewhat serious bit of code in quite a few years. Now I feel motivated to carry on developing it into something more widely useful.

## Roadmap

Currently working on a range of new features to make the library useful for real encryption applications.
These are mostly ways of introducing more variability into the output, making it more highly sensitive to small changes in input and also blending parts of the ciphertext into the key across progressive encoding 'frames' to make the algorithm more resistant to some attacks and keep the key more secure.
Additional features include:
- UTF-8 mode: works with variable width characters and uses a language dictionary to improve the space efficiency and security of encrypted text content.
- Binary mode: uses more generic compression and other approaches suitable for encrypting any binary data.
- Size masking: crypographically pads the ciphered data to mask the size of the unciphered data. 

These updates should be ready before the end of the year..

![Plot of rz mapping function, a part of upcoming features to improve quality of encryption](https://github.com/joe312213/Season/blob/main/rz_map_upcoming_feature.png)
