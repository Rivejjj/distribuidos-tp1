import logging
from filter_manager import FilterManager
from utils.initialize import init, initialize_config


def initialize():
    all_params = ["category",
                  "published_year_range", "title_contains", "save_books", "is_equal", "no_send"]

    params = list(map(lambda param: (param, False), all_params))

    filter_config_params = initialize_config(params)

    if filter_config_params["published_year_range"]:
        filter_config_params["published_year_range"] = tuple(
            map(int, filter_config_params["published_year_range"].split("-")))

    if filter_config_params["save_books"]:
        filter_config_params["save_books"] = True

    config_params = init(logging)

    config_params.update(filter_config_params)
    return config_params


def main():

    config_params = initialize()

    manager = FilterManager(config_params)

    manager.run()


if __name__ == "__main__":
    main()
