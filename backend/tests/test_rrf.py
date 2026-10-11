from backend.app.retrieval.rrf import reciprocal_rank_fusion


def test_rrf_prefers_item_in_both_lists():
    fused = reciprocal_rank_fusion([["a", "b"], ["b", "c"]])
    assert fused[0][0] == "b"
    assert fused[0][1] > fused[1][1]
