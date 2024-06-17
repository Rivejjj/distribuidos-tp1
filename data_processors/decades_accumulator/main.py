
import logging
from data_processors.decades_accumulator.accumulator_manager import AccumulatorManager
from utils.initialize import init


def main():

    config_params = init(logging)

    manager = AccumulatorManager(config_params)

    manager.run()


if __name__ == "__main__":
    main()
