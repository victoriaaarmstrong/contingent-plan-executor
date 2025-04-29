FROM python:3.9

WORKDIR /root/app

RUN pip install requests
RUN pip install Flask
RUN pip install Flask-SQLAlchemy
RUN pip install flask-cors
RUN pip install json2html
RUN pip install jsonpickle
RUN pip install nltk
RUN pip install textblob
RUN BLIS_ARCH="generic" pip install spacy --no-binary blis
RUN pip install graphviz
RUN pip install rstr==3.2.0

RUN python -m spacy download en_core_web_md

COPY contingent_plan_executor/ ./contingent_plan_executor

RUN rm -rf ./contingent_plan_executor/instance

COPY local_data/ ./local_data

ENTRYPOINT ["python", "./contingent_plan_executor/app.py"]