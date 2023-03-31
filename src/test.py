import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles


@cocotb.test()
async def test_basic(dut):
    dut._log.info("start")
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    dut._log.info("reset")
    dut.write_en.value = 0
    dut.reset_n.value = 0
    dut.pop.value = 0
    dut.peek.value = 0
    await ClockCycles(dut.clk, 10, False)
    dut.reset_n.value = 1

    assert dut.empty_n.value == 0
    assert dut.data_out.value == 0
    assert dut.ready.value == 0
    await ClockCycles(dut.clk, 1, False)
    assert dut.ready.value == 1

    # Push
    dut.write_en.value = 1
    dut.data_in.value = 63
    await ClockCycles(dut.clk, 1, False)
    assert dut.ready.value == 1
    
    # Peek
    dut.write_en.value = 0
    await ClockCycles(dut.clk, 2, False)
    assert dut.empty_n.value == 1
    assert dut.data_out.value == 63
    assert dut.ready.value == 1

    # Pop
    dut.pop.value = 1
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 0
    assert dut.data_out.value == 63
    assert dut.ready.value == 1

    # Pop clears
    dut.pop.value = 0
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 0
    assert dut.data_out.value == 0
    assert dut.ready.value == 1

    # Add 9 entries to FIFO
    dut.write_en.value = 1
    for i in range(9):
        dut.data_in.value = 1 + 3*i
        await ClockCycles(dut.clk, 1, False)
        assert dut.empty_n == (0 if i == 0 else 1)
        assert dut.ready.value == 1

    # Peek each entry in peek range
    dut.write_en.value = 0    
    for i in range(4):
        dut.peek.value = i
        await ClockCycles(dut.clk, 1, False)
        assert dut.data_out.value == 1 + 3*i
        assert dut.empty_n == 1
        assert dut.ready.value == 1

    # Pop each entry
    dut.peek.value = 0
    dut.pop.value = 1
    for i in range(9):
        await ClockCycles(dut.clk, 1, False)
        assert dut.data_out.value == 1 + 3*i
        assert dut.empty_n == 0 if i == 9 else 1
        assert dut.ready.value == 1

    # Pop clears
    dut.pop.value = 0
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 0
    assert dut.data_out.value == 0
    assert dut.ready.value == 1

    # Overfill the FIFO
    dut.write_en.value = 1
    for i in range(55):
        dut.data_in.value = 1 + i
        await ClockCycles(dut.clk, 1, False)
        assert dut.empty_n == (0 if i == 0 else 1)
        assert dut.ready.value == (1 if i < 51 else 0)

    # Peek each entry
    dut.write_en.value = 0
    for i in range(4):
        dut.peek.value = i
        await ClockCycles(dut.clk, 1, False)
        assert dut.data_out.value == 1 + i
        assert dut.empty_n == 1
        assert dut.ready.value == 0

    # Pop each entry
    dut.peek.value = 0
    dut.pop.value = 1
    for i in range(52):
        await ClockCycles(dut.clk, 1, False)
        assert dut.data_out.value == 1 + i
        assert dut.empty_n == 0 if i == 51 else 1
        assert dut.ready.value == (0 if i < 47 else 1)

    # Pop clears
    dut.pop.value = 0
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 0
    assert dut.data_out.value == 0
    assert dut.ready.value == 1

    # Pop when empty
    dut.pop.value = 1
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 0
    assert dut.data_out.value == 0
    assert dut.ready.value == 1

    dut.pop.value = 0
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 0
    assert dut.data_out.value == 0
    assert dut.ready.value == 1

    # Check FIFO still works
    dut.write_en.value = 1
    for i in range(20):
        dut.data_in.value = 1 + 2*i
        await ClockCycles(dut.clk, 1, False)
        assert dut.empty_n == (0 if i == 0 else 1)
        assert dut.ready.value == 1

    # Peek each entry
    dut.write_en.value = 0
    for i in range(4):
        dut.peek.value = i
        await ClockCycles(dut.clk, 1, False)
        assert dut.data_out.value == 1 + 2*i
        assert dut.empty_n == 1
        assert dut.ready.value == 1

    # Pop each entry
    dut.peek.value = 0
    dut.pop.value = 1
    for i in range(20):
        await ClockCycles(dut.clk, 1, False)
        assert dut.data_out.value == 1 + 2*i
        assert dut.empty_n == 0 if i == 19 else 1
        assert dut.ready.value == 1

    # Pop clears
    dut.pop.value = 0
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 0
    assert dut.data_out.value == 0
    assert dut.ready.value == 1

@cocotb.test()
async def test_full(dut):
    dut._log.info("start")
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    dut._log.info("reset")
    dut.write_en.value = 0
    dut.reset_n.value = 0
    dut.pop.value = 0
    dut.peek.value = 0
    await ClockCycles(dut.clk, 10, False)
    dut.reset_n.value = 1

    assert dut.empty_n.value == 0
    assert dut.data_out.value == 0
    assert dut.ready.value == 0
    await ClockCycles(dut.clk, 1, False)
    assert dut.ready.value == 1

    # Overfill the FIFO
    dut.write_en.value = 1
    for i in range(55):
        dut.data_in.value = 1 + i
        await ClockCycles(dut.clk, 1, False)
        assert dut.empty_n == (0 if i == 0 else 1)
        assert dut.ready.value == (1 if i < 51 else 0)

    for i in range(1,49):
        dut.write_en.value = 0

        # Pop some
        for j in range(i):
            dut.pop.value = 1
            await ClockCycles(dut.clk, 1, False)
            assert dut.empty_n.value == 1
            if dut.ready.value == 1: print(j)
            assert dut.ready.value == (0 if j < 47 else 1)

        # Ready takes 47 cycles
        dut.pop.value = 0
        if i < 48:
            await ClockCycles(dut.clk, 47-i, False)
            assert dut.ready.value == 0
        await ClockCycles(dut.clk, 1, False)
        assert dut.ready.value == 1

        # Refill
        dut.write_en.value = 1
        for j in range(i):
            dut.data_in.value = 1 + j
            await ClockCycles(dut.clk, 1, False)
            assert dut.empty_n == 1
            assert dut.ready.value == (1 if j < i-1 else 0)

@cocotb.test()
async def test_single_write_read(dut):
    dut._log.info("start")
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    dut._log.info("reset")
    dut.write_en.value = 0
    dut.reset_n.value = 0
    dut.pop.value = 0
    dut.peek.value = 0
    await ClockCycles(dut.clk, 10, False)
    dut.reset_n.value = 1
    await ClockCycles(dut.clk, 1, False)

    for i in range(5,52):
        #print("Testing at fullness {}".format(i))
        data = []

        # Fill FIFO to have i entries
        dut.write_en.value = 1
        for j in range(i):
            dut.data_in.value = 1 + j
            data.append(1 + j)
            await ClockCycles(dut.clk, 1, False)
            assert dut.empty_n == (0 if j == 0 else 1)
            assert dut.ready.value == 1

        # Repeatedly write one entry and read one entry
        for j in range(200):
            # Push
            dut.write_en.value = 1
            dut.data_in.value = j % 64
            data.append(j % 64)
            await ClockCycles(dut.clk, 1, False)
            assert dut.empty_n.value == 1
            
            # Pop
            dut.write_en.value = 0
            dut.pop.value = 1
            await ClockCycles(dut.clk, 1, False)
            dut.pop.value = 0
            assert dut.data_out.value == data[0]
            data.pop(0)
            assert dut.empty_n.value == (0 if i == 0 else 1)

            for k in range(49):
                if dut.ready.value == 1: 
                    #if k != 0: print("Fullness {} Iter {} waited {} cycles for ready".format(i, j, k))
                    break
                await ClockCycles(dut.clk, 1, False)
            assert dut.ready.value == 1

        # Clear the FIFO
        dut.pop.value = 1
        await ClockCycles(dut.clk, j, False)
        assert dut.empty_n == 0
        assert dut.ready.value == 1
