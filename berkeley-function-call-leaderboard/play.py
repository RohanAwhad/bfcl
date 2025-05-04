from types import SimpleNamespace

from bfcl._llm_response_generation import main as generation_main
from bfcl.constants.eval_config import RESULT_PATH, SCORE_PATH
from bfcl.eval_checker.eval_runner import main as evaluation_main

model = "Qwen/Qwen2.5-7B-Instruct-Turbo"
test_category = ["live_simple", "live_multiple", "live_parallel", "live_parallel_multiple"]
result_dir = RESULT_PATH
score_dir = SCORE_PATH

args = SimpleNamespace(
    model = model,
    test_category = test_category,
    # below are defaults takes from bfcl/__main__.py
    temperature=0.001,
    include_input_log=True,
    exclude_state_log=False,
    num_gpus=1,
    num_threads=1,
    gpu_memory_utilization=0.9,
    backend='openai',
    skip_server_setup=True,
    local_model_path=None,
    result_dir=result_dir,
    allow_overwrite=False,
    run_ids=False,
)
generation_main(args)


print('Running evaluation ...')
evaluation_main([model], test_category, result_dir, score_dir)
