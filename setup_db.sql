CREATE TABLE reference_data (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ref_source NVARCHAR(255),
    source_field NVARCHAR(255),
    source_value NVARCHAR(255),
    target_field NVARCHAR(255),
    target_value NVARCHAR(255),
    comments NVARCHAR(MAX),
    sha_hash NVARCHAR(64) UNIQUE
);
