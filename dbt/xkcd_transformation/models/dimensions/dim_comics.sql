{{ config(materialized='table') }}

SELECT      (data ->> 'num')::int as comic_id
            ,data ->> 'title' as title
            ,data ->> 'alt' as alt
            ,data ->> 'safe_title' as safe_title
            ,data ->> 'transcript' as transcript
            ,data ->> 'img' as image_url
            ,TO_DATE(
                (data ->> 'year') || '-' || (data ->> 'month') || '-' || (data ->> 'day'),
                'YYYY-MM-DD'
            ) as released_date
FROM        {{ source('public', 'raw_data') }}
ORDER BY    comic_id