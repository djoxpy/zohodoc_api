
<br/>
<div>

# ZohoDoc XLSX API
<p>
This program is designed to automatically download, compare, and analyze data from a Zoho XLSX document, then send the results to Telegram.


  


</p>
</div>

## About The Project

This project automates the process of downloading, comparing, and analyzing data from a Zoho XLSX document, with the final results being sent to a Telegram chat. The program ensures efficient data tracking and reporting by periodically retrieving updates and processing changes

<b>Key Features:</b>

- Automated Data Retrieval: Fetches data from a specified Zoho XLSX document using API authentication.
- Data Comparison & Analysis: Compares the latest data with the previously stored dataset to identify changes.
- Scheduled Execution: Runs at user-defined intervals, defaulting to every 12 hours.
- Telegram Integration: Sends processed results directly to a Telegram chat for easy monitoring.
### Built With

- [Python](https://www.python.org/)
- [Pip](https://pypi.org/project/pip/)
- [Docker](https://www.docker.com/)
## Getting Started

Get <b>CLIENT_ID</b> and <b>CLIENT_SECRET</b> from  https://api-console.zoho.com/

Get <b>PORTAL</b> number from Zoho

<b>PROJECT_NAME</b> is the name of the project where the XLSX table for tracking changes is located

<b>FILE_NAME</b> is the name of the XLSX table for tracking changes
### Prerequisites

- python

- pip

- Docker (optional)

### Installation

<h4>Local Installation</h4>

1. Clone the repository:
  ```sh
   git clone https://github.com/djoxpy/zohodoc_api.git
  ```
2. Navigate to the project directory:
  ```sh
   cd zohodoc_api/
  ```
3. Install dependencies:
  ```sh
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Enter your CLIENT_ID, CLIENT_SECRET, PORTAL, PROJECT_NAME, FILE_NAME in the `.env` file:
  ```js
   CLIENT_ID=1004.DCAJ27VKACCGNEPOYF04EVAR1FU7EW
   CLIENT_SECRET=90496a1c9efa37c677293dc02cfa54ac2fadb92625
   PORTAL=192000692
   PROJECT_NAME=Template
   FILE_NAME=Template.xlsx
  ```

<h4>Docker Installation</h4>

1. Set the custom update interval before building the Docker image:

  ```sh
  CMD ["python", "./run.py", "--first", "--interval", "6", "start"]
  ```

2.  Build the Docker image:
   ```sh
   docker build -t zohodoc_api .
   ```

## Usage

   <h4>Local Usage</h4>

   ```sh
   run.py [-h] [--first ] [--interval [12]] start
   ```
Running the program for the first time:
   ```sh
   run.py --first start
   #follow the instructions in the terminal
  ```

Running the program:
  ```sh
  run.py start
  ```
Running the program with a custom update interval:
  ```sh
  run.py --interval 12 start
  ```

 <h4>Docker Usage</h4>

1.  Run the Docker container:
   ```sh
   docker run -it zohodoc_api
   #follow the instructions in the terminal
   ```

2. Detach container terminal:
  ```sh
  Ctrl + P
  Ctrl + Q
  ```

## Roadmap

- [ ] Add Logging
- [ ] Add Notification of program failure
- [ ] Add Interactive instalator

See the [open issues](https://github.com/djoxpy/zohodoc_api/issues) for a full list of proposed features (and known issues).
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
## License

Distributed under the MIT License. See [MIT License](https://opensource.org/licenses/MIT) for more information.
## Contact

Ivan Bondar - ivan@bondar.work

Project Link: [zohodoc_api](https://github.com/djoxpy/zohodoc_api)
