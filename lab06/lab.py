import sys
from http009 import http_response

import typing
import doctest

sys.setrecursionlimit(10000)

# NO ADDITIONAL IMPORTS!


# custom exception types for lab 6


class HTTPRuntimeError(Exception):
    pass


class HTTPFileNotFoundError(FileNotFoundError):
    pass


# functions for lab 6
def status(f, url):
    """
    Handles redirects and/or exceptions. Either an error is 
    returned or the file and url that was successfully
    connected to is returned. 
    """

    if f.status in [301, 302, 307]:
        return status(http_response(f.getheader("location")),f.getheader("location"))
    elif f.status == 404:
        raise HTTPFileNotFoundError
    elif f.status == 500:
        raise HTTPRuntimeError
    else:
        return f, "success", url

"""def peek(f):
    pos = f.tell()
    out = f.readline()
    f.seek(pos)
    return out
"""
def manifest_w_cache(f):
    """
    Helper function to handle manifested files with caching support
    Returns a generator which we yield from in download_file

    """
    cached = {}
    while True:
        url_list = []
        
        while True:
            url = f.readline()
            if url == b"--\n" or url == b'':
                break
            else:
                url_list.append(url)
        if url_list == []:
            break

        if b'(*)\n' in url_list: #cache the file in the dictionary
            for url in url_list:
                if url in cached:
                    yield cached[url]
                    break
                if url == b'(*)\n':
                    continue
                else:
                    try:
                        
                        f_new , my_status, url_new = status(http_response(url), url)
                        if my_status == "success":
                            out = f_new.read()
                            cached[url_new] = out
                            print("cached: ", url_new)
                            yield out
                            break
                    except (ConnectionError, HTTPRuntimeError, HTTPFileNotFoundError, AssertionError) as e:
                        continue

        else:
            for url in url_list:
                if url in cached:
                    yield cached[url]
                    break
                try:
                    f_new , my_status, url_new = status(http_response(url), url)
                    if my_status == "success":
                        out = f_new.read()
                        print("noncached: ",url_new)
                        yield out
                        break
                except (ConnectionError, HTTPRuntimeError, HTTPFileNotFoundError, AssertionError) as e:
                    continue
"""def manifest(f):
    while True:
        url_list = []
        
        while True:
            url = f.readline()
            
            if url == b"--\n" or url == b'':
                break
            else:
                url_list.append(url)
    
        if url_list == []:
            break
        
        for url in url_list:
            try:
                f_new , my_status, url = status(http_response(url), url)
                if my_status == "success":
                    out = f_new.read()
                    #print('out', out)
                    yield out
                    break
            except (ConnectionError, HTTPRuntimeError, HTTPFileNotFoundError) as e:
                continue
"""              
      
def download_file(url, chunk_size=8192):
    """
    Yield the raw data from the given URL, in segments of at most chunk_size
    bytes (except when retrieving cached data as seen in section 2.2.1 of the
    writeup, in which cases longer segments can be yielded).

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises an HTTPRuntimeError if the URL can't be reached, or in the case of a
    500 status code.  Raises an HTTPFileNotFoundError in the case of a 404
    status code.
    """
    try:
        f = http_response(url)
        f_new, my_status, my_url = status(f, url)
        
        if my_status == "success":
            if f_new.getheader("content-type") == "text/parts-manifest" or my_url[-6:] == ".parts":
                print("reached here")
                yield from manifest_w_cache(f_new)                  
            else:
                while True:
                    out = f_new.read(chunk_size)
                    yield out
                    if out == b'':
                        break
        else:
            return my_status
    except ConnectionError:
        raise HTTPRuntimeError

    '''with open(url, 'rb') as f:
    
        while True:
            x = f.read(chunk_size)
            yield x
    '''

def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.
    """

    ends = b''
    for chunk in stream:
        chunk = ends + chunk
        ends = b''
        while True:
            if len(chunk) > 4: #get the number of bytes in the file
                byte_num = chunk[:4]
                num = int.from_bytes(byte_num, 'big')
                if len(chunk) >= 4 + num:                    
                    file = chunk[4:4 + num]
                    yield file
                    chunk = chunk[4 + num:]
                else:
                    ends += chunk
                    break
            else: #add the end to the beginning of the next stream
                ends += chunk
                break
    


if __name__ == "__main__":
    _, url , filename = sys.argv
    f = download_file(url)
    out = open(filename, 'wb')
    seq = files_from_sequence(f)
    '''while True:
        if next(f) != StopIteration:
            out.write(next(f)) 
        else:
            break
        '''
    a = 0
    for i in seq:
        a+=1
        if a == 53:
            out.write(i)
    #for i in f:
     #   out.write(i)
    out.close()