from test.utils import setUp, tearDown

import pytest
import pytest_asyncio

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def znc():
    proc, reader, writer = await setUp()
    yield (reader, writer)
    await tearDown(proc)
