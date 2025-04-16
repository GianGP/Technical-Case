{{ config(materialized='incremental', unique_key='comic_id') }}

SELECT  gen_random_uuid() as fct_comic_id,
        (data->>'num')::int as comic_id,
        5 * length(regexp_replace(data->>'title', '[^A-Za-z]', '', 'g')) as cost,
        floor(random() * 10000)::int as views,
        round((random() * 9 + 1)::numeric, 1) as reviews,
        now() as created_at
FROM    {{ source('public', 'raw_data') }}
{% if is_incremental() %}
WHERE   (data->>'num')::int not in (select comic_id from {{ this }})
{% endif %}