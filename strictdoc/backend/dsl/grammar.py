STRICTDOC_GRAMMAR = """
Document:
  '[DOCUMENT]' 
  'NAME:' name = /.*$/
  sections *= SectionOrRequirement
;

SectionOrRequirement:
  Section | Requirement
;

Section:
  '[SECTION]' 
  'LEVEL:' level = INT
  'TITLE:' title = /.*$/ 
  section_contents *= SectionOrRequirement
;

Requirement:
  '[REQUIREMENT]'

  ('UID:' uid = /.*$/)?

  ('REFS:' references *= Reference)?

  ('TITLE:' title = /.*$/)?

  'STATEMENT:' statement = /.*$/

  ('BODY:' 
    body = Body
  )?

  comments *= ReqComment
;

ReqComment:
  'COMMENT:' comment = /.*$/
;

Body:
    content = /(?ms)>>>(.*?)<<</
;

Reference:
  '-' 'TYPE:' file_type = "File"
      'VALUE:' path = /.*$/
;
"""
