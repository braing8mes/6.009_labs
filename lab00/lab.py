# No Imports Allowed!


def backwards(sound):
    '''a = sound.copy()
    a['samples'] = a['samples'].reverse()
    return a'''
    return {'rate': sound['rate'],
    'samples': sound['samples'][::-1] }

def mix(sound1, sound2, p):
    if sound1['rate'] != sound2['rate']:
        return None
    else:
        num_sam = min(len(sound1['samples']), len(sound2['samples']))
        mixsound = []
        for i in range (num_sam):
            mixsound.append(sound1['samples'][i]*p + sound2['samples'][i]*(1-p))
        return {'rate': sound1['rate'],
    'samples':mixsound }


def convolve(sound, kernel):
    convolve_samples = [0]*(len(sound['samples'])+len(kernel)-1)
    for i in range(len(kernel)):
        
        for j in range(len(sound['samples'])):
            convolve_samples[i+j] += sound['samples'][j]*kernel[i]
    return {'rate': sound['rate'], 'samples': convolve_samples}

def echo(sound, num_echoes, delay, scale):
    echo_samples = [0] * (len(sound['samples']) + round(delay*sound['rate'])*num_echoes)
    for i in range(num_echoes+1):
        shift = i*round(delay*sound['rate']) #each subsequent echo shifted over by sample_delay
        b = scale ** i #scale factor
        for j in range(len(sound['samples'])):
            echo_samples[shift+j] += b * sound['samples'][j]
    return {'rate': sound['rate'], 'samples': echo_samples}


def pan(sound):
    N = len(sound['left'])
    l = []
    r = []
    
    for i in range(N):
        b = i/(N-1)
        c = 1-i/(N-1)
        l.append(c*sound['left'][i])
        r.append(b*sound['right'][i])
    return {'rate': sound['rate'], 'left': l, 'right': r}

def remove_vocals(sound):
    #a = [sound['left'][i]-sound['right'][i] for (sound['left'][i], sound['right'][i]) in zip(sound['left'],sound['right'])]
    a=[]
    for i in range (len(sound['left'])):
        a.append(sound['left'][i]-sound['right'][i])
    return {'rate': sound['rate'], 'samples': a}


def bass_boost_kernel(N, scale=0):
    """
    Construct a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    kernel = {'rate': 0, 'samples': [0.25, 0.5, 0.25]}
    for i in range(N):
        kernel = convolve(kernel, base['samples'])
    kernel = kernel['samples']

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel)//2] += 1

    return kernel


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {'rate': sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack('<h', frame[:2])[0])
                right.append(struct.unpack('<h', frame[2:])[0])
            else:
                datum = struct.unpack('<h', frame)[0]
                left.append(datum)
                right.append(datum)

        out['left'] = [i/(2**15) for i in left]
        out['right'] = [i/(2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack('<h', frame[:2])[0]
                right = struct.unpack('<h', frame[2:])[0]
                samples.append((left + right)/2)
            else:
                datum = struct.unpack('<h', frame)[0]
                samples.append(datum)

        out['samples'] = [i/(2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')

    if 'samples' in sound:
        # mono file
        outfile.setparams((1, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = [int(max(-1, min(1, v)) * (2**15-1)) for v in sound['samples']]
    else:
        # stereo
        outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))
        out = []
        for l, r in zip(sound['left'], sound['right']):
            l = int(max(-1, min(1, l)) * (2**15-1))
            r = int(max(-1, min(1, r)) * (2**15-1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    hello = load_wav('sounds/hello.wav')
    synth = load_wav('sounds/synth.wav')
    water = load_wav('sounds/water.wav')
    mystery = load_wav('sounds/mystery.wav')
    #write_wav(mix(synth, water, 0.2), 'mixed.wav')
    #mykernel = bass_boost_kernel(1000, 1.5)
    ice = load_wav('sounds/ice_and_chilli.wav')
    chord = load_wav('sounds/chord.wav')
    car = load_wav('sounds/car.wav', stereo = True)
    mount = load_wav('sounds/lookout_mountain.wav',stereo= True)
    write_wav(remove_vocals(mount), 'mount_voiceless.wav')
    #write_wav(pan(car),'panned_car.wav')
    #write_wav(echo(chord, 5,0.3,0.6), 'echo_chord.wav')
    #write_wav(convolve(ice, mykernel),'bass_boost_ice.wav')
    #write_wav(backwards(mystery), 'yretsym.wav')
    #write_wav(backwards(hello), 'hello_reversed.wav')
