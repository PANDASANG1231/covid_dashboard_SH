# dashboard_omicron_SH

Because of Omicron, Shanghai is right now locked down. I love Shanghai because I was borned there. Also, I have seen so many informations online that is seeking for help. As a result, I want to build up a demo dashboard to monitor all those information and provide the visualization. God bless Shanghai.

Functions:

- Monitor the historical data of information since the locking down.
- Monitor the omicron data, and try to figure out what type of information is the most important topic.

## Authur

Wenjia Zhu, Current student in the University of British Columbia.

## Usage
  - Makefile: make start
  - Dockerfile:
    
    1. docker pull zwj63518583/env_dashboard:latest
    2. docker run --rm -it -v /$(pwd):/home zwj63518583/env_dashboard:latest make -C /home start

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`dashboard_omicron_SH` was created by Wenjia Zhu. It is licensed under the terms of the MIT license.

## Credits

`dashboard_omicron_SH` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
