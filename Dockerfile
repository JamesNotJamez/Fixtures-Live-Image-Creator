FROM python:3.8

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
	# Adding Google Chrome to the repositories
	sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
	# Updating apt to see and install Google Chrome
	apt-get -y update && \
	apt-get install -y google-chrome-stable && \
	# Installing Unzip
	apt-get install -yqq unzip && \
	# Download the Chrome Driver 
	wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_linux64.zip && \
	# Unzip the Chrome Driver into /usr/local/bin directory
	unzip -q /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Set display port as an environment variable
ENV DISPLAY=:99

WORKDIR /app

# Copy requirements in and install
COPY ./requirements.txt /app
RUN pip install --upgrade pip; \ 
	pip install -r requirements.txt

# Copy rest of app contents in
COPY . /app

CMD ["python", "./app.py"]
