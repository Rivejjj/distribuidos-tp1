import time
from common.client import Client
from utils.initialize import decode, initialize_config, initialize_log


def initialize():

    config_params = initialize_config(
        [("logging_level", True), ("address", True), ("port", True), ("books_path", False), ("books_reviews_path", False)])

    config_params["port"] = int(config_params["port"])
    initialize_log(config_params["logging_level"])
    return config_params


def run(config_params):
    client = Client(config_params["address"], config_params["port"])
    time.sleep(40)

    # with open('results.csv', 'w') as a:
    with open(config_params["books_path"]) as file:
        i = 0
        for line in file:
            print(line.strip())
            client.send_message(line.strip())
            if i == 1000:
                break
            i += 1
            # msg = decode(client.receive_message())

            # print(msg)

            # a.write(msg + '\n')

        print(i)
    # with open(config_params["books_reviews_path"]) as file:
    #     i = 0
    #     for line in file:
    #         print(line.strip())
    #         client.send_message(line.strip())
    #         if i == 10000:
    #             break
    #         i += 1
    client.send_message("EOF")

    while True:
        msg = decode(client.receive_message())
        if msg == "EOF":
            break
        number, text = msg.split(':', 1)
        filename = f"query{number}.txt"
        with open(filename, 'a') as f:
            f.write(text + '\n')

    client.stop()


def main():
    config_params = initialize()
    print(config_params)
    run(config_params)


if __name__ == "__main__":
    main()
