FROM python:3.9.5

COPY . .

ENV GUROBI_HOME=/gurobi951/linux64
ENV LD_LIBRARY_PATH=/gurobi951/linux64/lib
ENV PATH="${PATH}:${GUROBI_HOME}/bin"
ENV GRB_LICENSE_FILE=/home/gurobi.lic

RUN pip3 install -r requirements.txt

CMD ["python3", "-m" , "runner.py", "First problem", "C20", "1dat.txt"]
