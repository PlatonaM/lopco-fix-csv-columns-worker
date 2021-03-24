"""
   Copyright 2021 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


import os
import uuid
import requests


dep_instance = os.getenv("DEP_INSTANCE")
job_callback_url = os.getenv("JOB_CALLBACK_URL")
input_file = os.getenv("source_csv")
delimiter = os.getenv("delimiter")
ref_header = set(os.getenv("reference_header").split(delimiter)) if os.getenv("reference_header") else None
abort_on_unknown = int(os.getenv("abort_on_unknown"))
abort_on_missing = int(os.getenv("abort_on_missing"))
data_cache_path = "/data_cache"


def abort(reason):
    print(reason)
    print("aborting ...")
    exit()


def print_head(file, num=5):
    with open("{}/{}".format(data_cache_path, file), "r") as f:
        count = 0
        for line in f:
            if count >= num:
                break
            print(line.strip())
            count += 1


print("checking columns ...")

with open("{}/{}".format(data_cache_path, input_file), "r") as file:
    header = file.readline().strip().split(delimiter)

if not ref_header.intersection(set(header)):
    abort("no column of header in reference header")

unknown_cols = set(header) - ref_header
missing_cols = ref_header - set(header)

if unknown_cols and abort_on_unknown:
    abort("unknown columns: {}".format(", ".join(unknown_cols)))

if missing_cols and abort_on_missing:
    abort("missing columns: {}".format(", ".join(missing_cols)))

output_file = input_file

if unknown_cols or missing_cols:
    intermediate = False
    if unknown_cols:
        print("removing unknown columns: {}".format(", ".join(unknown_cols)))
        unknown_cols_pos = set()
        for col in unknown_cols:
            unknown_cols_pos.add(header.index(col))
        line_range = range(len(header))
        output_file = uuid.uuid4().hex
        with open("{}/{}".format(data_cache_path, input_file), "r") as in_file:
            with open("{}/{}".format(data_cache_path, output_file), "w") as out_file:
                line_count = 0
                for line in in_file:
                    line = line.strip().split(delimiter)
                    new_line = list()
                    for pos in line_range:
                        if pos not in unknown_cols_pos:
                            new_line.append(line[pos])
                    if len(new_line) == 1 and not new_line[0]:
                        pass
                    else:
                        out_file.write(delimiter.join(new_line) + "\n")
                    line_count += 1
        print_head(output_file)
        print("total number of lines written: {}".format(line_count))
        input_file = output_file
        intermediate = True
    if missing_cols:
        print("adding missing columns: {}".format(", ".join(missing_cols)))
        output_file = uuid.uuid4().hex
        padding = delimiter * len(missing_cols)
        with open("{}/{}".format(data_cache_path, input_file), "r") as in_file:
            with open("{}/{}".format(data_cache_path, output_file), "w") as out_file:
                line = in_file.readline().strip()
                out_file.write(line + delimiter + delimiter.join(missing_cols) + "\n")
                line_count = 1
                for line in in_file:
                    line = line.strip()
                    out_file.write(line + padding + "\n")
                    line_count += 1
        print_head(output_file)
        print("total number of lines written: {}".format(line_count))
        if intermediate:
            os.remove("{}/{}".format(data_cache_path, input_file))
else:
    print("nothing to do")

try:
    resp = requests.post(
        job_callback_url,
        json={dep_instance: {"output_file": output_file}}
    )
    if not resp.ok:
        raise RuntimeError(resp.status_code)
except Exception as ex:
    try:
        os.remove("{}/{}".format(data_cache_path, output_file))
    except Exception:
        pass
    raise ex
