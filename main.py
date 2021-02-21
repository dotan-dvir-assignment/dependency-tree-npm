from flask import Flask
from flask_restful import Resource, Api, reqparse
import requests
import multiprocessing
import threading

active_threads = 0
package_cache = dict()
in_progress = set()
work_queue = list()
lock = threading.Lock()
processor_count = multiprocessing.cpu_count()
app = Flask(__name__)
api = Api(app)

def download_package_info(package_name, package_version="latest"):
    # download the information from the registry
    try:
        response = requests.get("https://registry.npmjs.org/{0}/{1}".format(package_name, package_version))

        if response.status_code != 200:
            return None, None,None

        json_output = response.json()

        return json_output["name"], json_output["version"], json_output.get("dependencies", None)

    except Exception as ex:
        print(ex)
        return None, None, None





def parse_version_string(version_string):
    if version_string == None or len(version_string) == 0:
        return None

    if version_string[0] == "^" or version_string[0] == "~":
        return version_string[1:]

    return version_string


def process_package(name, version, depedencies):
    package_info = package_cache.get(name, {})
    package_version = package_info.get(version)
    top_level_list  = list()

    if package_version is None:
        lock.acquire()
        package_info[version] = depedencies
        package_cache[name] = package_info

        in_progress.remove(name+":"+version)

        if depedencies is None:
            lock.release()
            return

        for dependency, version in depedencies.items():
            version = parse_version_string(version)
            dependency_cache = package_cache.get(dependency, {})
            version_cache = dependency_cache.get(version, None)
            in_progress_cache = (dependency+":"+version) in in_progress

            if version_cache is None and in_progress_cache is False:
                in_progress.add(dependency+":"+version)

                work_queue.append((dependency, parse_version_string(version)))
        lock.release()


def worker_thread():
    while True:
        lock.acquire()

        if len(work_queue)>0:
            work_item = work_queue.pop()
            lock.release()

            try:
                name, version, dependencies = download_package_info(work_item[0], work_item[1])

                if name is None or version is None:
                    continue
            except:
                pass

            process_package(name,version,dependencies)
        else:
            lock.release()
            break


def start_threads():
    for i in range(processor_count):
        t = threading.Thread(target=worker_thread, args=())
        t.start()
        t.join()


def download_all_dependencies(package_name):
    if package_name is None or len(package_name) == 0:
        return False,"Wrong package name provided"

    name, version, dependencies = download_package_info(package_name)

    if name is None or version is None:
        return False,"Could not locate package"

    in_progress.add(name+":"+version)
    process_package(name, version, dependencies)
    start_threads()
    return True,"OK"


def print_tree_level(package_name,version,level):
    ret = "\t" * level +package_name+":"+version + "\n"

    try:
        dependencies = package_cache[package_name][version]
    except:
        return ret

    if dependencies is None:
        return ret

    for dep,dep_version in dependencies.items():
        ret+= print_tree_level(dep,parse_version_string(dep_version),level+1)

    return ret


def print_tree(package_name):
    main_package = package_cache[package_name]

    for version in main_package.keys():
        return print_tree_level(package_name,version,0)

@app.route('/<package_name>')
def process_request(package_name):
    success,message = download_all_dependencies(package_name)

    if success is False:
        return message,400

    return print_tree(package_name),200



if __name__ == '__main__':
    app.run()