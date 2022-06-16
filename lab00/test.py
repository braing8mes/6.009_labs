#!/usr/bin/env python3

import os
import copy
import pickle

import pytest

import lab

TEST_DIRECTORY = os.path.dirname(__file__)


def compare_sounds(result, expected, eps=1e-6):
    # well formed?
    assert isinstance(result['rate'], int), 'Sampling rate should be an integer'
    if 'left' in result:
        assert len(result['left']) == len(result['right']), 'Left and Right channels do not have the same length'

    # matches expected?
    assert result['rate'] == expected['rate'], 'Sampling rates do not match'


    # compare (different for stereo vs mono)
    if 'left' in result:
        assert 'left' in expected, "Expected mono sound, got stereo"
        assert len(result['left']) == len(expected['left']), 'Lengths do not match'
        for ix, ((res_l, res_r), (exp_l, exp_r)) in enumerate(zip(zip(result['left'], result['right']), zip(expected['left'], expected['right']))):
            assert abs(res_l-exp_l) <= eps and abs(res_r-exp_r) < eps, f'Values at index {ix} do not match.'
    else:
        assert 'samples' in expected, "Expected stereo sound, got mono"
        assert len(result['samples']) == len(expected['samples']), 'Lengths do not match'
        for ix, (res, exp) in enumerate(zip(result['samples'], expected['samples'])):
            assert abs(res-exp) <= eps, f'Values at index {ix} do not match.'



def compare_against_file(x, fname, stereo=False):
    compare_sounds(x, lab.load_wav(fname, stereo=stereo), eps=(2/(2**15-1)))

def load_pickle_pair(name):
    with open(os.path.join(TEST_DIRECTORY, 'test_inputs', name), 'rb') as f:
        with open(os.path.join(TEST_DIRECTORY, 'test_outputs', name), 'rb') as f2:
            return (pickle.load(f), pickle.load(f2))


def test_backwards_small():
    inp = {
        'rate': 20,
        'samples': [1,2,3,4,5,6],
    }
    inp2 = copy.deepcopy(inp)
    out = {
        'rate': 20,
        'samples': [6,5,4,3,2,1],
    }
    compare_sounds(lab.backwards(inp), out)
    assert inp == inp2, 'be careful not to modify the input!'


def test_backwards_real():
    inp = lab.load_wav(os.path.join(TEST_DIRECTORY, 'sounds', 'hello.wav'))
    inp2 = copy.deepcopy(inp)
    outfile = os.path.join(TEST_DIRECTORY, 'test_outputs', 'hello_backwards.wav')
    compare_against_file(lab.backwards(inp), outfile)
    assert inp == inp2, 'be careful not to modify the input!'

@pytest.mark.parametrize('test_number', [1, 2])
def test_backwards_random(test_number):
    inps, exp = load_pickle_pair('backwards_%02d.pickle' % test_number)
    inps2 = copy.deepcopy(inps)
    compare_sounds(lab.backwards(*inps), exp)
    assert inps == inps2, 'be careful not to modify the input!'


def test_mix_small():
    s1 = {
        'rate': 30,
        'samples': [1,2,3,4,5,6],
    }
    s2 = {
        'rate': 20,
        'samples': [1,2,3,4,5,6],
    }
    s3 = {
        'rate': 30,
        'samples': [7, 8, 9, 10],
    }

    s4 = {
        'rate': 30,
        'samples': [0.7+2.1, 1.4+2.4, 2.1+2.7, 2.8+3.0],
    }

    assert lab.mix(s1, s2, 0.5) is None
    compare_sounds(lab.mix(s1, s3, 0.7), s4)


def test_mix_real():
    inp1 = lab.load_wav(os.path.join(TEST_DIRECTORY, 'sounds', 'chord.wav'))
    inp2 = lab.load_wav(os.path.join(TEST_DIRECTORY, 'sounds', 'crash.wav'))
    inp3 = copy.deepcopy(inp1)
    inp4 = copy.deepcopy(inp2)

    res = lab.mix(inp1, inp2, 0.35)
    outfile = os.path.join(TEST_DIRECTORY, 'test_outputs', 'chord_crash.wav')
    compare_against_file(res, outfile)

    assert inp1 == inp3, 'be careful not to modify the input!'
    assert inp2 == inp4, 'be careful not to modify the input!'


@pytest.mark.parametrize('test_number', [1, 2])
def test_mix_random(test_number):
    inps, exp = load_pickle_pair('mix_%02d.pickle' % test_number)
    inps2 = copy.deepcopy(inps)
    compare_sounds(lab.mix(*inps), exp)
    assert inps == inps2, 'be careful not to modify the inputs!'


def test_convolve_small():
    inp = {
        'rate': 7,
        'samples': [1, 2, 3],
    }
    inp2 = copy.deepcopy(inp)
    exp = {
        'rate': 7,
        'samples': [1, 0, -1, -6],
    }
    compare_sounds(lab.convolve(inp, [1,-2]), exp)
    assert inp == inp2, 'be careful not to modify the inputs!'


@pytest.mark.parametrize('test_number', [1, 2, 3, 4])
def test_convolve_random(test_number):
    inps, exp = load_pickle_pair('convolve_%02d.pickle' % test_number)
    inps2 = copy.deepcopy(inps)
    compare_sounds(lab.convolve(*inps), exp)
    assert inps == inps2, 'be careful not to modify the inputs!'


def test_convolve_real():
    kern = lab.bass_boost_kernel(2, 100)
    kern[len(kern)//2] -= 1
    for ix in range(len(kern)):
        kern[ix] *= (-1)**ix
    inp = lab.load_wav(os.path.join(TEST_DIRECTORY, 'sounds', 'hello.wav'))
    inp2 = copy.deepcopy(inp)
    outfile = os.path.join(TEST_DIRECTORY, 'test_outputs', 'hello_hpf.wav')
    compare_against_file(lab.convolve(inp, kern), outfile)
    assert inp == inp2, 'be careful not to modify the input!'


def test_echo_small():
    inp = {
        'rate': 9,
        'samples': [1, 2, 3],
    }
    inp2 = copy.deepcopy(inp)
    exp = {
        'rate': 9,
        'samples': [1,2,3, 0,0, 0.7,1.4,2.1, 0,0, 0.49,0.98,1.47],
    }
    compare_sounds(lab.echo(inp, 2, 0.6, 0.7), exp)
    assert inp == inp2, 'be careful not to modify the inputs!'


def test_echo_real():
    inp = lab.load_wav(os.path.join(TEST_DIRECTORY, 'sounds', 'synth.wav'))
    inp2 = copy.deepcopy(inp)
    outfile = os.path.join(TEST_DIRECTORY, 'test_outputs', 'synth_echo.wav')
    compare_against_file(lab.echo(inp, 6, 0.5, 0.7), outfile)
    assert inp == inp2, 'be careful not to modify the input!'


@pytest.mark.parametrize('test_number', [1, 2])
def test_echo_random(test_number):
    inps, exp = load_pickle_pair('echo_%02d.pickle' % test_number)
    inps2 = copy.deepcopy(inps)
    compare_sounds(lab.echo(*inps), exp)
    assert inps == inps2, 'be careful not to modify the inputs!'


def test_pan_small():
    inp = {
        'rate': 42,
        'left': [4, 4, 4, 4, 4],
        'right': [6, 6, 6, 6, 6],
    }
    inp2 = copy.deepcopy(inp)
    exp = {
        'rate': 42,
        'left': [4, 3, 2, 1, 0],
        'right': [0, 1.5, 3, 4.5, 6],
    }
    compare_sounds(lab.pan(inp), exp)
    assert inp == inp2, 'be careful not to modify the input!'


def test_pan_real():
    inp = lab.load_wav(os.path.join(TEST_DIRECTORY, 'sounds', 'mystery.wav'), stereo=True)
    inp2 = copy.deepcopy(inp)
    outfile = os.path.join(TEST_DIRECTORY, 'test_outputs', 'mystery_pan.wav')
    compare_against_file(lab.pan(inp), outfile, stereo=True)
    assert inp == inp2, 'be careful not to modify the input!'


@pytest.mark.parametrize('test_number', [1, 2])
def test_pan_random(test_number):
    inps, exp = load_pickle_pair('pan_%02d.pickle' % test_number)
    inps2 = copy.deepcopy(inps)
    compare_sounds(lab.pan(*inps), exp)
    assert inps == inps2, 'be careful not to modify the input!'


def test_remove_vocals_small():
    inp = {
        'rate': 30,
        'left': [7, 9, 3, 4],
        'right': [12, 2, 9, 2],
    }
    inp2 = copy.deepcopy(inp)
    exp = {
        'rate': 30,
        'samples': [-5, 7, -6, 2],
    }
    compare_sounds(lab.remove_vocals(inp), exp)
    assert inp == inp2, 'be careful not to modify the input!'


@pytest.mark.parametrize('test_number', [1, 2, 3])
def test_remove_vocals_random(test_number):
    inps, exp = load_pickle_pair('remove_vocals_%02d.pickle' % test_number)
    inps2 = copy.deepcopy(inps)
    compare_sounds(lab.remove_vocals(*inps), exp)
    assert inps == inps2, 'be careful not to modify the input!'


if __name__ == '__main__':
    import os
    import sys
    import json
    import pickle
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--gather", action='store_true')
    parser.add_argument("--server", action='store_true')
    parser.add_argument("--initial", action='store_true')
    parser.add_argument("args", nargs="*")

    parsed = parser.parse_args()

    class TestData:
        def __init__(self, gather=False):
            self.alltests = None
            self.results = {'passed': []}
            self.gather = gather

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtestloop(self, session):
            yield

        def pytest_runtest_logreport(self, report):
            if report.when != 'call':
                return
            self.results.setdefault(report.outcome, []).append(report.head_line)

        def pytest_collection_finish(self, session):
            if self.gather:
                self.alltests = [i.name for i in session.items]


    pytest_args = ['-v', __file__]

    if parsed.server:
        pytest_args.insert(0, '--color=yes')

    if parsed.gather:
        pytest_args.insert(0, '--collect-only')

    testinfo = TestData(parsed.gather)
    res = pytest.main(
        ['-k', ' or '.join(parsed.args), *pytest_args],
        **{'plugins': [testinfo]}
    )

    if parsed.server:
        _dir = os.path.dirname(__file__)
        if parsed.gather:
            with open(os.path.join(_dir, 'alltests.json'), 'w' if parsed.initial else 'a') as f:
                f.write(json.dumps(testinfo.alltests))
                f.write('\n')
        else:
            with open(os.path.join(_dir, 'results.json'), 'w' if parsed.initial else 'a') as f:
                f.write(json.dumps(testinfo.results))
                f.write('\n')
