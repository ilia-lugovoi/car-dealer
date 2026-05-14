CREATE TABLE IF NOT EXISTS v_medium
(
    medium_name String,
    medium_group_id Int32,
    medium_sort Int32
)
ENGINE = MergeTree
ORDER BY medium_sort;
