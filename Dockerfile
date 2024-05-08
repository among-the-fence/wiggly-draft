FROM gorialis/discord.py:slim-buster-master-minimal

WORKDIR /

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
COPY .git/ ./.git/

CMD ["python", "main.py"]