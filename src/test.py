import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ClockCycles


@cocotb.test()
async def test_fifo(dut):
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

    # Push
    dut.write_en.value = 1
    dut.data_in.value = 63
    await ClockCycles(dut.clk, 1, False)
    
    # Peek
    dut.write_en.value = 0
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 1
    assert dut.data_out.value == 63

    # Pop
    dut.pop.value = 1
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 0
    assert dut.data_out.value == 63

    # Pop clears
    dut.pop.value = 0
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 0
    assert dut.data_out.value == 0

    # Add 9 entries to FIFO
    dut.write_en.value = 1
    for i in range(9):
        dut.data_in.value = 1 + 3*i
        await ClockCycles(dut.clk, 1, False)
        assert dut.empty_n == 1

    # Peek each entry
    dut.write_en.value = 0    
    for i in range(9):
        dut.peek.value = i
        await ClockCycles(dut.clk, 1, False)
        assert dut.data_out.value == 1 + 3*i
        assert dut.empty_n == 1

    # Pop each entry
    dut.peek.value = 0
    dut.pop.value = 1
    for i in range(9):
        await ClockCycles(dut.clk, 1, False)
        assert dut.data_out.value == 1 + 3*i
        assert dut.empty_n == 0 if i == 9 else 1

    # Pop clears
    dut.pop.value = 0
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 0
    assert dut.data_out.value == 0

    # Overfill the FIFO
    dut.write_en.value = 1
    for i in range(20):
        dut.data_in.value = 1 + 2*i
        await ClockCycles(dut.clk, 1, False)
        assert dut.empty_n == 1

    # Peek each entry
    dut.write_en.value = 0
    for i in range(16):
        dut.peek.value = i
        await ClockCycles(dut.clk, 1, False)
        assert dut.data_out.value == 1 + 2*i
        assert dut.empty_n == 1

    # Pop each entry
    dut.peek.value = 0
    dut.pop.value = 1
    for i in range(16):
        await ClockCycles(dut.clk, 1, False)
        assert dut.data_out.value == 1 + 2*i
        assert dut.empty_n == 0 if i == 15 else 1

    # Pop clears
    dut.pop.value = 0
    await ClockCycles(dut.clk, 1, False)
    assert dut.empty_n.value == 0
    assert dut.data_out.value == 0

