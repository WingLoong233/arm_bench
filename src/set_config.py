import json
import os

cur_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    path_dic = {
        "path": {
            "access_memory": cur_dir + "/test_load_store2/parse/perf-post.csv",
            "access_function": cur_dir + "/test_icache_iTLB/parse/perf-post.csv",
            "branch_prediction": cur_dir + "/test_branch_miss/parse/perf-post.csv",
            "arithm2": cur_dir + "/test_cpi2/parse/perf-post.csv",
            "profile": cur_dir + "/profile.json"
        }
    }
    with open(cur_dir + "/align/config.json", "w") as f:
        json.dump(path_dic, f)
