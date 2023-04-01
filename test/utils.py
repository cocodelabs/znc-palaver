import asyncio
import os
from typing import Dict, Optional, Tuple

import pytest
from semantic_version import Version


async def setUp():
    running_as_root = os.getuid() == 0
    allow_root = ' --allow-root' if running_as_root else ''

    proc = await asyncio.create_subprocess_shell(
        f'znc -d test/fixtures --foreground --debug{allow_root}'
    )
    await asyncio.sleep(31 if running_as_root else 1)

    (reader, writer) = await asyncio.open_connection('localhost', 6698)
    writer.write(b'CAP LS 302\r\n')

    line = await reader.readline()
    writer.write(b'CAP REQ :palaverapp.com\r\n')

    line = await reader.readline()
    assert line == b':irc.znc.in CAP unknown-nick ACK :palaverapp.com\r\n'

    writer.write(b'CAP END\r\n')
    writer.write(b'PASS admin\r\n')
    writer.write(b'USER admin admin admin\r\n')
    writer.write(b'NICK admin\r\n')
    await writer.drain()

    line = await reader.readline()
    assert line == b':irc.znc.in 001 admin :Welcome to ZNC\r\n'

    return (proc, reader, writer)


async def tearDown(proc):
    await asyncio.sleep(0.2)

    proc.kill()
    await proc.wait()

    config = 'test/fixtures/moddata/palaver/palaver.conf'
    if os.path.exists(config):
        os.remove(config)


async def get_znc_version():
    proc = await asyncio.create_subprocess_shell(
        'znc --version', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()
    return stdout.decode('utf-8').split()[1]


async def requires_znc_version(znc_version):
    actual_version = await get_znc_version()

    if Version(znc_version) > Version(actual_version):
        pytest.skip(
            'ZNC >= {} is required for this test, found {}'.format(znc_version, version)
        )


async def read_headers(reader) -> Dict[str, str]:
    headers = {}

    while True:
        line = await reader.readline()
        if line == b'\r\n':
            return headers

        name, _, value = line.decode('utf-8').strip().partition(': ')
        # while HTTP allows the multiple headers wiht the same name,
        # we're keeping implementation simple by not handling that
        # case (because we don't use it).
        assert name not in headers

        headers[name] = value


async def read_push_request(reader) -> Tuple[Dict[str, str], bytes]:
    request_line = await reader.readline()
    assert request_line == b'POST /push HTTP/1.1\r\n'

    headers = await read_headers(reader)
    assert headers['Host'] == '127.0.0.1'
    assert headers['Connection'] == 'close'
    assert headers['Content-Type'] == 'application/json'
    await assert_user_agent(headers['User-Agent'])

    assert 'Content-Length' in headers
    body = await reader.read(int(headers['Content-Length']))
    return headers, body


async def assert_user_agent(user_agent):
    products = user_agent.split(' ')
    assert len(products) == 2

    product1, product1_version = products[0].split('/')
    assert product1 == 'znc-palaver'
    assert Version(product1_version).major >= 1

    product2, product2_version = products[1].split('/')
    assert product2 == 'znc'
    assert product2_version == await get_znc_version()
