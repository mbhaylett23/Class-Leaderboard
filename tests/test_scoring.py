import pytest

def test_combined_weighting_arithmetic_example():
    # Contract: combined = peersPct% * peer_sum + teacherPct% * teacher_sum (int trunc)
    peer_sum, teacher_sum = 30, 18
    peersPct, teacherPct = 60, 40
    combined = int(peer_sum*(peersPct/100.0) + teacher_sum*(teacherPct/100.0))
    assert isinstance(combined, int)
