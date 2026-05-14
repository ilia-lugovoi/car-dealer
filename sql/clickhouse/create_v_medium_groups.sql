CREATE TABLE IF NOT EXISTS v_medium_groups
(
    medium_group_name String,
    medium_group_sort Int32
)
ENGINE = MergeTree
ORDER BY medium_group_sort;
