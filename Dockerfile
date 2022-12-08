FROM gorialis/discord.py:slim-buster-master-minimal

WORKDIR /

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]