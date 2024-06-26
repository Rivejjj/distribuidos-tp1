import yaml

WORKERS = 4
CLIENTS = 3
MONITORS = 3
LOGGING_LEVEL = 'INFO'


def create_docker_compose():
    with open(f"docker-compose-dev.yaml", "w") as file:
        config = {
            'name': 'tp1',
            'services': {}
        }

        # config['services']['rabbitmq'] = build_rabbitmq()
        for i in range(CLIENTS):
            config['services'][f'sender_client_{i}'] = build_client(i)

        for i in range(MONITORS):
            config['services'][f'monitor{i}'] = build_monitor(i)

        config['services']['gateway'] = build_gateway()

        build_query1(config['services'])
        build_query2(config['services'])
        build_query3(config['services'])
        build_query4(config['services'])
        build_query5(config['services'])

        # config['networks'] = build_network()

        yaml.dump(config, file, sort_keys=False)


def build_rabbitmq():
    return {
        'container_name': 'rabbit',
        'build': {
            'context': './rabbitmq',
            'dockerfile': 'rabbitmq.dockerfile'
        },
        'ports': [
            '15672:15672'
        ],
        'healthcheck': {
            'test': ['CMD', 'curl', '-f', 'http://localhost:15672/'],
            'interval': '10s',
            'timeout': '5s',
            'retries': 10
        }
    }


def build_gateway():

    return {
        'container_name': 'gateway',
        'image': 'gateway:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            f'OUTPUT_QUEUES=query1:{WORKERS};query2:{WORKERS};query3:{WORKERS};query4:{WORKERS}',
            'INPUT_QUEUE=results',
            f'QUERY_COUNT={WORKERS+WORKERS+WORKERS+2}',
            'ID=0',
            f'NAME=gateway'
        ],

    }


def build_client(i):
    return {
        'container_name': f'sender_client_{i}',
        'image': 'client:latest',
        'entrypoint': 'python3 /main.py',
        'depends_on': [
            'gateway'
        ],
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'BOOKS_PATH=/data/books_data_reduced.csv',
            'BOOKS_REVIEWS_PATH=/data/Books_rating_reduced.csv',
            f'ID={i}'
        ],
        'volumes': [
            './data/csv:/data',
            f'./data/{i}/query:/query'
        ],

    }


def build_query1(config_services):
    for i in range(WORKERS):
        config_services[f'computers_category_filter_{i}'] = build_computer_category_filter(
            i)

    for i in range(WORKERS):
        config_services[f'2000s_published_year_filter_{i}'] = build_2000s_published_year_filter(
            i)

    for i in range(WORKERS):
        config_services[f'title_contains_filter_{i}'] = build_title_contains_filter(
            i)


def build_query2(config_services):
    for i in range(WORKERS):
        config_services[f'decades_accumulator_{i}'] = build_decades_accumulator(
            i)


def build_query3(config_services):
    for i in range(WORKERS):
        config_services[f'1990s_published_year_filter_{i}'] = build_1990s_published_year_filter(
            i)

    for i in range(WORKERS):
        config_services[f'reviews_counter_{i}'] = build_reviews_counter(
            i)


def build_query4(config_services):
    config_services['avg_rating_accumulator'] = build_avg_rating_accumulator()


def build_query5(config_services):
    for i in range(WORKERS):
        config_services[f'fiction_category_filter_{i}'] = build_fiction_category_filter(
            i)

    for i in range(WORKERS):
        config_services[f'sentiment_analyzer_{i}'] = build_sentiment_analyzer(
            i)
    config_services['sentiment_score_accumulator'] = build_sentiment_score_accumulator()


def build_computer_category_filter(i):
    container_name = f'computers_category_filter_{i}'
    return {
        'container_name': container_name,
        'image': 'book_filter:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'INPUT_QUEUE=query1',
            f'OUTPUT_QUEUES=computers:{WORKERS}',
            'CATEGORY=Computers',
            f'ID={i}',
            'IS_EQUAL=True',
            f'NAME={container_name}'
        ],
        'volumes': [
            f'./data/checkpoint/{container_name}:/.checkpoints'
        ],

    }


def build_2000s_published_year_filter(i):
    container_name = f'2000s_published_year_filter_{i}'
    return {
        'container_name': container_name,
        'image': 'book_filter:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'INPUT_QUEUE=computers',
            f'OUTPUT_QUEUES=2000s_filtered:{WORKERS}',
            'PUBLISHED_YEAR_RANGE=2000-2023',
            f'ID={i}',
            f'PREVIOUS_WORKERS={WORKERS}',
            f'NAME={container_name}'
        ],
        'volumes': [
            f'./data/checkpoint/{container_name}:/.checkpoints'
        ],

    }


def build_title_contains_filter(i):
    container_name = f'title_contains_filter_{i}'
    return {
        'container_name': container_name,
        'image': 'book_filter:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'INPUT_QUEUE=2000s_filtered',
            f'OUTPUT_QUEUES=results:1',
            'TITLE_CONTAINS=distributed',
            f'ID={i}',
            'QUERY=1',
            f'PREVIOUS_WORKERS={WORKERS}',
            f'NAME={container_name}'
        ],
        'volumes': [
            f'./data/checkpoint/{container_name}:/.checkpoints'
        ],


    }


def build_decades_accumulator(i):
    container_name = f'decades_accumulator_{i}'
    return {
        'container_name': container_name,
        'image': 'decades_accumulator:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'INPUT_QUEUE=query2',
            'OUTPUT_QUEUES=results:1',
            'TOP=10',
            f'ID={i}',
            'QUERY=2',
            f'NAME={container_name}'
        ],
        'volumes': [
            f'./data/checkpoint/{container_name}:/.checkpoints'
        ],

    }


def build_1990s_published_year_filter(i):
    container_name = f'1990s_published_year_filter_{i}'
    return {
        'container_name': container_name,
        'image': 'book_filter:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'INPUT_QUEUE=query3',
            f'OUTPUT_QUEUES=90s_filtered:{WORKERS}',
            'PUBLISHED_YEAR_RANGE=1990-1999',
            f'ID={i}',
            'SAVE_BOOKS=True',
            f'NAME={container_name}'
        ],
        'volumes': [
            f'./data/checkpoint/{container_name}:/.checkpoints'
        ],
    }


def build_reviews_counter(i):
    container_name = f'reviews_counter_{i}'
    return {
        'container_name': container_name,
        'image': 'reviews_counter_accum:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'INPUT_QUEUE=90s_filtered',
            'OUTPUT_QUEUES=500_reviews:1;results:1',
            f'ID={i}',
            'QUERY=3',
            f'PREVIOUS_WORKERS={WORKERS}',
            f'NAME={container_name}'
        ],
        'volumes': [
            f'./data/checkpoint/{container_name}:/.checkpoints'
        ],
    }


def build_avg_rating_accumulator():
    container_name = 'avg_rating_accumulator'
    return {
        'container_name': container_name,
        'image': 'top_rating_accumulator:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'INPUT_QUEUE=500_reviews',
            'OUTPUT_QUEUES=results:1',
            'ID=0',
            'QUERY=4',
            f'PREVIOUS_WORKERS={WORKERS}',
            f'NAME={container_name}'
        ],
        'volumes': [
            f'./data/checkpoint/{container_name}:/.checkpoints'
        ],

    }


def build_fiction_category_filter(i):
    container_name = f'fiction_category_filter_{i}'
    return {
        'container_name': container_name,
        'image': 'book_filter:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'INPUT_QUEUE=query4',
            f'OUTPUT_QUEUES=fiction:{WORKERS}',
            'CATEGORY=fiction',
            f'ID={i}',
            'SAVE_BOOKS=True',
            'NO_SEND=True',
            f'NAME={container_name}'
        ],
        'volumes': [
            f'./data/checkpoint/{container_name}:/.checkpoints'
        ],

    }


def build_sentiment_analyzer(i):
    container_name = f'sentiment_analyzer_{i}'
    return {
        'container_name': container_name,
        'image': 'sentiment_analyzer:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'INPUT_QUEUE=fiction',
            f'OUTPUT_QUEUES=sentiment_score:1',
            f'ID={i}',
            f'PREVIOUS_WORKERS={WORKERS}',
            f'NAME={container_name}'
        ],
        'volumes': [
            f'./data/checkpoint/{container_name}:/.checkpoints'
        ],

    }


def build_sentiment_score_accumulator():
    container_name = 'sentiment_score_accumulator'
    return {
        'container_name': container_name,
        'image': 'sentiment_score_accumulator:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            f'LOGGING_LEVEL={LOGGING_LEVEL}',
            'INPUT_QUEUE=sentiment_score',
            'OUTPUT_QUEUES=results:1',
            'ID=0',
            'QUERY=5',
            f'PREVIOUS_WORKERS={WORKERS}',
            f'NAME={container_name}'
        ],
        'volumes': [
            f'./data/checkpoint/{container_name}:/.checkpoints'
        ],

    }


def build_network():
    return {
        'testing_net': {
            'ipam': {
                'driver': 'default',
                'config': [
                    {
                        'subnet': '172.25.125.0/24'
                    }
                ]
            }
        }
    }


def build_monitor(i):
    container_name = f'monitor{i}'
    return {
        "container_name": container_name,
        "image": 'monitor:latest',
        "privileged": True,
        "entrypoint": 'python3 /main.py',
        "environment": [
            f'ID={i}',
            f'NAME={container_name}',
            f'WORKERS={",".join(generate_all_workers())}'
        ],
        "volumes": ['/var/run/docker.sock:/var/run/docker.sock']
    }


def generate_all_workers():
    worker_names = [
        'computers_category_filter',
        '2000s_published_year_filter',
        'title_contains_filter',
        'decades_accumulator',
        '1990s_published_year_filter',
        'reviews_counter',
        'fiction_category_filter',
        'sentiment_analyzer',
    ]
    all_worker_names = [
        f'{name}_{worker}' for name in worker_names for worker in range(WORKERS)]

    all_worker_names.append('avg_rating_accumulator')
    all_worker_names.append('sentiment_score_accumulator')
    all_worker_names.append('gateway')
    return all_worker_names


def create_atomic_bomb():
    with open('atomic_bomb.sh', 'w') as f:
        f.write('#!/bin/bash\n')

        workers = generate_all_workers()

        workers.remove('gateway')

        f.write(f'docker kill {" ".join(workers)}\n')


def main():
    create_docker_compose()
    create_atomic_bomb()


if __name__ == "__main__":
    main()
