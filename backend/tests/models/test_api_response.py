from app.models.api_response import ApiResponse


def test_defaults_success_true_and_empty_metadata() -> None:
    resp = ApiResponse(data={"a": 1})
    assert resp.success is True
    assert resp.metadata == {}
    assert resp.timestamp


def test_data_can_be_any_json_serializable_shape() -> None:
    assert ApiResponse(data=[1, 2, 3]).data == [1, 2, 3]
    assert ApiResponse(data="hello").data == "hello"


def test_metadata_can_be_overridden() -> None:
    resp = ApiResponse(data={}, metadata={"page": 1})
    assert resp.metadata == {"page": 1}


def test_model_dump_json_produces_expected_keys() -> None:
    resp = ApiResponse(data={"x": 1})
    dumped = resp.model_dump()
    assert set(dumped.keys()) == {"success", "data", "metadata", "timestamp"}
