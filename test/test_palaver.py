import asyncio
import json
from test.utils import (
    assert_user_agent,
    get_znc_version,
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


async def test_registering_device(znc):
    reader, writer = znc

    writer.write(
        b'PALAVER IDENTIFY 9167e47b01598af7423e2ecd3d0a3ec4 611d3a30a3d666fc491cdea0d2e1dd6e b758eaab1a4611a310642a6e8419fbff\r\n'
    )
    await writer.drain()

    line = await reader.readline()
    assert line == b'PALAVER REQ *\r\n'

    writer.write(
        b'PALAVER BEGIN 9167e47b01598af7423e2ecd3d0a3ec4 611d3a30a3d666fc491cdea0d2e1dd6e\r\n'
    )
    writer.write(b'PALAVER SET PUSH-TOKEN 605b64f5addc408fcfa7ff0685e2d065fdecb127\r\n')
    writer.write(b'PALAVER SET PUSH-ENDPOINT https://api.palaverapp.com/1/push\r\n')
    writer.write(b'PALAVER ADD MENTION-KEYWORD cocode\r\n')
    writer.write(b'PALAVER ADD MENTION-KEYWORD {nick}\r\n')
    writer.write(b'PALAVER END\r\n')
    await writer.drain()


async def test_loading_module_new_cap():
    await requires_znc_version('1.7.0')

    (proc, reader, writer) = await setUp()

    writer.write(b'PRIVMSG *status :unloadmod palaver\r\n')
    await writer.drain()

    line = await reader.readline()
    assert line == b':irc.znc.in CAP admin DEL :palaverapp.com\r\n'

    line = await reader.readline()
    assert line == b':*status!znc@znc.in PRIVMSG admin :Module palaver unloaded.\r\n'

    writer.write(b'PRIVMSG *status :loadmod palaver\r\n')
    await writer.drain()

    line = await reader.readline()
    assert line == b':irc.znc.in CAP admin NEW :palaverapp.com\r\n'

    line = await reader.readline()
    assert (
        line
        == b':*status!znc@znc.in PRIVMSG admin :Loaded module palaver: [test/fixtures/modules/palaver.so]\r\n'
    )

    await tearDown(proc)


async def test_unloading_module_del_cap():
    await requires_znc_version('1.7.0')

    (proc, reader, writer) = await setUp()

    writer.write(b'PRIVMSG *status :unloadmod palaver\r\n')
    await writer.drain()

    line = await reader.readline()
    assert line == b':irc.znc.in CAP admin DEL :palaverapp.com\r\n'

    line = await reader.readline()
    assert line == b':*status!znc@znc.in PRIVMSG admin :Module palaver unloaded.\r\n'

    await tearDown(proc)


async def test_receiving_notification(znc):
    reader, writer = znc

    async def connected(reader, writer):
        headers, body = await read_push_request(reader)
        assert headers['Authorization'] == 'Bearer 9167e47b01598af7423e2ecd3d0a3ec4'
        assert json.loads(body.decode('utf-8')) == {
            'badge': 1,
            'message': 'Test notification',
            'sender': 'palaver',
            'network': 'b758eaab1a4611a310642a6e8419fbff',
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
    await writer.drain()

    writer.write(b'PRIVMSG *palaver :test\r\n')
    await writer.drain()

    await asyncio.sleep(0.2)
    server.close()
    await server.wait_closed()

    assert connected.called


async def test_receiving_notification_with_push_token(znc):
    async def connected(reader, writer):
        headers, body = await read_push_request(reader)
        assert headers['Authorization'] == 'Bearer abcdefg'
        assert json.loads(body.decode('utf-8')) == {
            'badge': 1,
            'message': 'Test notification',
            'sender': 'palaver',
            'network': 'b758eaab1a4611a310642a6e8419fbff',
        }

        writer.write(b'HTTP/1.1 204 No Content\r\n\r\n')
        await writer.drain()
        writer.close()

        connected.called = True

    server = await asyncio.start_server(connected, host='127.0.0.1', port=0)
    await asyncio.sleep(0.2)
    addr = server.sockets[0].getsockname()
    url = f'http://{addr[0]}:{addr[1]}/push'

    reader, writer = znc
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
    writer.write(f'PALAVER SET PUSH-TOKEN abcdefg\r\n'.encode('utf-8'))
    writer.write(b'PALAVER END\r\n')
    await writer.drain()

    writer.write(b'PRIVMSG *palaver :test\r\n')
    await writer.drain()

    await asyncio.sleep(0.2)
    server.close()
    await server.wait_closed()

    assert connected.called


async def test_receiving_notification_with_retry_on_rate_limit(znc):
    reader, writer = znc

    async def connected(reader, writer):
        headers, body = await read_push_request(reader)
        assert headers['Authorization'] == 'Bearer abcdefg'
        assert json.loads(body.decode('utf-8')) == {
            'badge': 1,
            'message': 'Test notification',
            'sender': 'palaver',
            'network': 'b758eaab1a4611a310642a6e8419fbff',
        }

        if not hasattr(connected, 'requests'):
            connected.requests = 1
            writer.write(b'HTTP/1.1 429 Too Many Requests\r\n')
        else:
            connected.requests += 1
            writer.write(b'HTTP/1.1 204 No Content\r\n')

        writer.write(b'Connection: close\r\n')
        writer.write(b'\r\n')

        await writer.drain()
        writer.close()

    server = await asyncio.start_server(connected, host='127.0.0.1', port=8121)
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
    writer.write(f'PALAVER SET PUSH-TOKEN abcdefg\r\n'.encode('utf-8'))
    writer.write(b'PALAVER END\r\n')
    await writer.drain()

    writer.write(b'PRIVMSG *palaver :test\r\n')
    await writer.drain()

    line = await reader.readline()
    assert (
        line
        == b':*palaver!znc@znc.in PRIVMSG admin :Notification sent to 1 clients.\r\n'
    )

    await asyncio.sleep(2.2)
    server.close()
    await server.wait_closed()

    assert connected.requests == 2


async def test_receiving_notification_with_retry_on_server_error(znc):
    reader, writer = znc

    async def connected(reader, writer):
        headers, body = await read_push_request(reader)
        assert headers['Authorization'] == 'Bearer abcdefg'
        assert json.loads(body.decode('utf-8')) == {
            'badge': 1,
            'message': 'Test notification',
            'sender': 'palaver',
            'network': 'b758eaab1a4611a310642a6e8419fbff',
        }

        if not hasattr(connected, 'requests'):
            connected.requests = 1
            writer.write(b'HTTP/1.1 503 Service Unavailable\r\n')
        else:
            connected.requests += 1
            writer.write(b'HTTP/1.1 204 No Content\r\n')

        writer.write(b'Connection: close\r\n')
        writer.write(b'\r\n')

        await writer.drain()
        writer.close()

    server = await asyncio.start_server(connected, host='127.0.0.1', port=8121)
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
    writer.write(f'PALAVER SET PUSH-TOKEN abcdefg\r\n'.encode('utf-8'))
    writer.write(b'PALAVER END\r\n')
    await writer.drain()

    writer.write(b'PRIVMSG *palaver :test\r\n')
    await writer.drain()

    line = await reader.readline()
    assert (
        line
        == b':*palaver!znc@znc.in PRIVMSG admin :Notification sent to 1 clients.\r\n'
    )

    await asyncio.sleep(2.2)
    server.close()
    await server.wait_closed()

    assert connected.requests == 2


async def test_receiving_notification_with_retry_on_disconnect(znc):
    reader, writer = znc

    async def connected(reader, writer):
        if not hasattr(connected, 'requests'):
            connected.requests = 1
            writer.close()
            return

        headers, body = await read_push_request(reader)
        assert headers['Authorization'] == 'Bearer abcdefg'
        assert json.loads(body.decode('utf-8')) == {
            'badge': 1,
            'message': 'Test notification',
            'sender': 'palaver',
            'network': 'b758eaab1a4611a310642a6e8419fbff',
        }

        connected.requests += 1
        writer.write(b'HTTP/1.1 204 No Content\r\n')

        writer.write(b'Connection: close\r\n')
        writer.write(b'\r\n')

        await writer.drain()
        writer.close()

    server = await asyncio.start_server(connected, host='127.0.0.1', port=8121)
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
    writer.write(f'PALAVER SET PUSH-TOKEN abcdefg\r\n'.encode('utf-8'))
    writer.write(b'PALAVER END\r\n')
    await writer.drain()

    writer.write(b'PRIVMSG *palaver :test\r\n')
    await writer.drain()

    line = await reader.readline()
    assert (
        line
        == b':*palaver!znc@znc.in PRIVMSG admin :Notification sent to 1 clients.\r\n'
    )

    await asyncio.sleep(2.2)
    server.close()
    await server.wait_closed()

    assert connected.requests == 2
