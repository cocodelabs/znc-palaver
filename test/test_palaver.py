import time
import os
import asyncio
import pytest

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio

async def setUp(event_loop):
    proc = await asyncio.create_subprocess_shell('znc -d test/fixtures --foreground --debug', loop=event_loop)
    time.sleep(1)

    (reader, writer) = await asyncio.open_connection('localhost', 6698, loop=event_loop)
    writer.write(b'PASS admin\r\n')
    writer.write(b'USER admin admin admin\r\n')
    writer.write(b'NICK admin\r\n')
    await writer.drain()

    line = await reader.readline()
    assert line == b':irc.znc.in 001 admin :Welcome to ZNC\r\n'

    line = await reader.readline()
    assert line == b":*status!znc@znc.in PRIVMSG admin :You are currently disconnected from IRC. Use 'connect' to reconnect.\r\n"
    return (proc, reader, writer)

async def tearDown(proc):
    proc.kill()
    await proc.wait()

    os.remove('test/fixtures/moddata/palaver/palaver.conf')

async def test_registering_device(event_loop):
    (proc, reader, writer) = await setUp(event_loop)

    writer.write(b'PALAVER IDENTIFY 9167e47b01598af7423e2ecd3d0a3ec4 611d3a30a3d666fc491cdea0d2e1dd6e b758eaab1a4611a310642a6e8419fbff\r\n')
    await writer.drain()

    line = await reader.readline()
    assert line == b'PALAVER REQ *\r\n'

    writer.write(b'PALAVER BEGIN 9167e47b01598af7423e2ecd3d0a3ec4 611d3a30a3d666fc491cdea0d2e1dd6e\r\n')
    writer.write(b'PALAVER SET PUSH-TOKEN 605b64f5addc408fcfa7ff0685e2d065fdecb127\r\n')
    writer.write(b'PALAVER SET PUSH-ENDPOINT https://api.palaverapp.com/1/push\r\n')
    writer.write(b'PALAVER ADD MENTION-KEYWORD cocode\r\n')
    writer.write(b'PALAVER ADD MENTION-KEYWORD {nick}\r\n')
    writer.write(b'PALAVER END\r\n')
    await writer.drain()
    time.sleep(1)

    await tearDown(proc)
