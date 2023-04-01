import asyncio
import json
from test.utils import (
    assert_user_agent,
    get_znc_version,
    open_registered_znc_connection,
    read_headers,
    read_push_request,
    requires_znc_version,
    setUp,
    tearDown,
)

import pytest
import pytest_asyncio

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_receiving_broadcast(znc):
    reader, writer = znc

    async def connected(reader, writer):
        headers, body = await read_push_request(reader)
        assert headers['Authorization'] == 'Bearer 9167e47b01598af7423e2ecd3d0a3ec4'
        assert json.loads(body.decode('utf-8')) == {
            'badge': 1,
            'message': 'test',
            'sender': 'ZNC Admin',
        }

        writer.write(b'HTTP/1.1 204 No Content\r\n\r\n')
        await writer.drain()
        writer.close()

        connected.called = True

    server = await asyncio.start_server(connected, host='127.0.0.1', port=0)
    await asyncio.sleep(0.2)
    addr = server.sockets[0].getsockname()
    url = f'http://{addr[0]}:{addr[1]}/push'

    writer.write(
        b'PALAVER IDENTIFY 9167e47b01598af7423e2ecd3d0a3ec4 611d3a30a3d666fc491cdea0d2e1dd6e b758eaab1a4611a310642a6e8419fbff\r\n'
    )
    await writer.drain()

    line = await reader.readline()
    assert line == b'PALAVER REQ *\r\n'

    writer.write(
        b'PALAVER BEGIN 9167e47b01598af7423e2ecd3d0a3ec4 611d3a30a3d666fc491cdea0d2e1dd6e\r\n'
    )
    writer.write(f'PALAVER SET PUSH-ENDPOINT {url}\r\n'.encode('utf-8'))
    writer.write(b'PALAVER END\r\n')
    writer.write(b'QUIT :Bye\r\n')
    await writer.drain()
    writer.close()
    await writer.wait_closed()

    reader, writer = await open_registered_znc_connection()
    writer.write(b'PRIVMSG *status :broadcast test\r\n')
    await writer.drain()

    await asyncio.sleep(0.2)
    server.close()
    await server.wait_closed()

    assert connected.called
