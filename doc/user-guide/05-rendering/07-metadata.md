
## Document Metadata

Docma allows the template to control some of the metadata added to the final PDF
or HTML and enforces some values of its own.

PDF and HTML documents have slightly different conventions regarding metadata
naming and formatting. Docma handles these variations.

In HTML, the metadata fields are added into the `<HEAD>` of the final document
in this form:

```html
<meta content="Fred Nurk" name="author"/>
<meta content="A document about stuff" name="title"/>
<meta content="DRAFT, Top-Secret" name="keywords"/>
<meta content="2024-11-21T00:04:38.699978+00:00" name="creation_date"/>
```

In PDF, the meta data fields are used to populate the standard metadata elements
recognised by common PDF readers.

| HTML Naming    | PDF Naming    | Controlled by | Comments                                            |
|----------------|---------------|---------------|-----------------------------------------------------|
| author         | /Author       | Template      | From the `metadata->author` key in `config.yaml`    |
| creation\_date | /CreationDate | Docma         | Document production datetime                        |
| creator        | /Creator      | Docma         | Based on template `id`, `version` and docma version |
| keywords       | /Keywords     | Template      | From the `metadata->keywords` key in `config.yaml`  |
| subject        | /Subject      | Template      | From the `metadata->subject` key in `config.yaml`   |
| title          | /Title        | Template      | From the `metadata->title` key in `config.yaml`     |
