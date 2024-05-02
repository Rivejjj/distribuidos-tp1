import yaml
import sys

WORKERS = 3

pools = [('computers_category_filter', WORKERS),
         ('2000s_published_year_filter', WORKERS),
         ('title_contains_filter', WORKERS),
         ('decades-accumulator', WORKERS),
         ('1990s_published_year_filter', WORKERS),
         ('reviews_counter', WORKERS),
         ('avg_rating_accumulator', 1),
         ('fiction_category_filter', WORKERS),
         ('sentiment_analyzer', WORKERS),
         ('sentiment_score_accumulator', 1)
         ]


def create_docker_compose():
    with open(f"docker-compose-dev-1.yaml", "w") as file:
        config = {
            'name': 'tp1',
            'services': {}
        }

        # config['services']['rabbitmq'] = build_rabbitmq()
        config['services']['client'] = build_client()
        config['services']['gateway'] = build_gateway()

        build_query1(config['services'])
        build_query2(config['services'])
        build_query3(config['services'])
        build_query4(config['services'])
        build_query5(config['services'])

        config['networks'] = build_network()

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
            'LOGGING_LEVEL=INFO',
            f'OUTPUT_QUEUES=query1:{WORKERS};query2:{WORKERS};query3:{WORKERS};query4:{WORKERS}',
            'INPUT_QUEUE=results',
            f'QUERY_COUNT={WORKERS+WORKERS+WORKERS+2}',
            'ID=0'
        ],
        'networks': [
            'testing_net'
        ]

    }


def build_client():
    return {
        'container_name': 'client',
        'image': 'client:latest',
        'entrypoint': 'python3 /main.py',
        'depends_on': [
            'gateway'
        ],
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
            'BOOKS_PATH=/data/books_data.csv',
            'BOOKS_REVIEWS_PATH=/data/Books_rating.csv'
        ],
        'volumes': [
            './data:/data'
        ],
        'networks': [
            'testing_net'
        ]

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
        config_services[f'decades-accumulator_{i}'] = build_decades_accumulator(
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
    return {
        'container_name': f'computers_category_filter_{i}',
        'image': 'book-filter:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
            'INPUT_QUEUE=query1',
            f'OUTPUT_QUEUES=computers:{WORKERS}',
            'CATEGORY=Computers',
            f'ID={i}'
        ],
        'networks': [
            'testing_net'
        ]

    }


def build_2000s_published_year_filter(i):
    return {
        'container_name': f'2000s_published_year_filter_{i}',
        'image': 'book-filter:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
            'INPUT_QUEUE=computers',
            f'OUTPUT_QUEUES=2000s_filtered:{WORKERS}',
            'PUBLISHED_YEAR_RANGE=2000-2023',
            f'ID={i}',
            f'PREVIOUS_WORKERS={WORKERS}'
        ],
        'networks': [
            'testing_net'
        ]

    }


def build_title_contains_filter(i):
    return {
        'container_name': f'title_contains_filter_{i}',
        'image': 'book-filter:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
            'INPUT_QUEUE=2000s_filtered',
            f'OUTPUT_QUEUES=results:1',
            'TITLE_CONTAINS=distributed',
            f'ID={i}',
            'QUERY=1',
            f'PREVIOUS_WORKERS={WORKERS}'
        ],
        'networks': [
            'testing_net'
        ]


    }


def build_decades_accumulator(i):
    return {
        'container_name': f'decades-accumulator_{i}',
        'image': 'decades-accumulator:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
            'INPUT_QUEUE=query2',
            'OUTPUT_QUEUES=results:1',
            'TOP=10',
            f'ID={i}',
            'QUERY=2',
        ],
        'networks': [
            'testing_net'
        ]

    }


def build_1990s_published_year_filter(i):
    return {
        'container_name': f'1990s_published_year_filter_{i}',
        'image': 'book-filter:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
            'INPUT_QUEUE=query3',
            f'OUTPUT_QUEUES=90s_filtered:{WORKERS}',
            'PUBLISHED_YEAR_RANGE=1990-1999',
            f'ID={i}',
            'SAVE_BOOKS=True',
        ],
        'networks': [
            'testing_net'
        ]

    }


def build_reviews_counter(i):

    return {
        'container_name': f'reviews_counter_{i}',
        'image': 'reviews_counter_accum:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
            'INPUT_QUEUE=90s_filtered',
            'OUTPUT_QUEUES=500_reviews:1;results:1',
            f'ID={i}',
            'QUERY=3',
            f'PREVIOUS_WORKERS={WORKERS}'
        ],
        'networks': [
            'testing_net'
        ]


    }


def build_avg_rating_accumulator():
    return {
        'container_name': 'avg_rating_accumulator',
        'image': 'accumulator:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
            'INPUT_QUEUE=500_reviews',
            'OUTPUT_QUEUES=results:1',
            'ID=0',
            'QUERY=4',
            f'PREVIOUS_WORKERS={WORKERS}'
        ],
        'networks': [
            'testing_net'
        ]

    }


def build_fiction_category_filter(i):
    return {
        'container_name': f'fiction_category_filter_{i}',
        'image': 'book-filter:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
            'INPUT_QUEUE=query1',
            f'OUTPUT_QUEUES=fiction:{WORKERS}',
            'CATEGORY=Fiction',
            f'ID={i}',
            'SAVE_BOOKS=True'
        ],
        'networks': [
            'testing_net'
        ]

    }


def build_sentiment_analyzer(i):
    return {
        'container_name': f'sentiment_analyzer_{i}',
        'image': 'sentiment_analyzer:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
            'INPUT_QUEUE=fiction',
            f'OUTPUT_QUEUES=sentiment_score:1',
            f'ID={i}',
            f'PREVIOUS_WORKERS={WORKERS}'
        ],
        'networks': [
            'testing_net'
        ]

    }


def build_sentiment_score_accumulator():
    return {
        'container_name': 'sentiment_score_accumulator',
        'image': 'sentiment_score_accumulator:latest',
        'entrypoint': 'python3 /main.py',
        'environment': [
            'PYTHONUNBUFFERED=1',
            'LOGGING_LEVEL=INFO',
            'INPUT_QUEUE=sentiment_score',
            'OUTPUT_QUEUES=results:1',
            'ID=0',
            'QUERY=5',
            f'PREVIOUS_WORKERS={WORKERS}'
        ],
        'networks': [
            'testing_net'
        ]

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


def main():
    create_docker_compose()


if __name__ == "__main__":
    main()
