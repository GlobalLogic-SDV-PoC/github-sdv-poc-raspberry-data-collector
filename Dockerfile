FROM public.ecr.aws/docker/library/alpine:latest as base

RUN apk add --no-cache cmake gcc g++ ninja linux-headers

COPY ./ /var/work

RUN mkdir -p /var/work/build-folder && cd /var/work/build-folder && cmake -GNinja .. && cmake --build .

FROM public.ecr.aws/docker/library/alpine:latest as runtime

RUN apk add --no-cache libstdc++

ADD ./resources/configs /var/configs

COPY --from=base /var/work/build-folder/data_collection_app /usr/local/bin/

ENTRYPOINT ["/usr/local/bin/data_collection_app"]
