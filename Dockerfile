FROM cdrx/pyinstaller-linux:python3

# RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
# RUN rustc --version
# RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
COPY ./requirements.txt /tmp
# RUN PATH="$HOME/.cargo/bin:$PATH" && pip install -r /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install --ignore-installed apscheduler

