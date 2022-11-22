FROM sphinxdoc/sphinx
COPY ./app /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install autodocsumm myst-parser sphinxcontrib-mermaid furo