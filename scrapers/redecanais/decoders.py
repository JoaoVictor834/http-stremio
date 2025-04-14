# functions to decode obfuscated files and scripts

import base64
import re

import aiohttp


def decode_redecanais(payload: list[str], key: int):
    final_chars = []
    for b64_str in payload:
        try:
            # decode the base 64 string back to utf8
            decoded_str = base64.b64decode(b64_str).decode()

            # extract the integer representing the character
            encoded_char = int(re.sub(r"\D", "", decoded_str))

            # subtract the key to get the unicode value for the character
            encoded_char -= key

            # append charcter to final string
            final_chars.append(chr(encoded_char))

        except:
            continue

    # return the decoded content
    try:
        return "".join(final_chars).encode("latin1").decode("utf8")
    except UnicodeDecodeError:
        return "".join(final_chars)


async def decode_from_response(response: aiohttp.ClientResponse):
    print("decode_from_response")
    # iterate through the response and extract all the encoded strings
    prev_chunk = ""
    b64_list = []
    async for chunk in response.content.iter_chunked(1024):
        # extract b64 strings from current chunk plus what was left from the previous chunk
        curr_chunk = prev_chunk + chunk.decode()
        b64_strs = re.findall(r"((?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=))", curr_chunk)

        # remove all the b64 strings from the current chunk and save it as previous chunk
        # also remove empty strings and whitespaces
        prev_chunk = re.sub(r"(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)", "", curr_chunk)
        prev_chunk = re.sub(r'( |\n)*"",', "", prev_chunk)

        # save all b64 strings to the list
        [b64_list.append(s) for s in b64_strs]

    # extract key from what was left from prev_chunk
    key = re.findall(r".replace.* *?- *?(\d+)\)", prev_chunk)
    if key:
        key = int(key[0])

    return decode_redecanais(b64_list, key)
