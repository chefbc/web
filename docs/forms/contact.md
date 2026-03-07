---
title: Contact Us
layout: form
form_config:
  webhook_url: https://hooks.zapier.com/hooks/catch/12345/abcde
  on_success:
    type: message
    value: Thank you! We've received your message.
  fields:
  - name: name
    label: Full Name
    type: text
    placeholder: Jane Doe
    required: true
  - name: email
    label: Email Address
    type: email
    placeholder: jane@example.com
    required: true
  - name: subject
    label: Subject
    type: select
    options:
    - label: General Inquiry
      value: general
    - label: Support
      value: support
    - label: Feedback
      value: feedback
    required: true
  - name: message
    label: Your Message
    type: textarea
    placeholder: How can we help?
    required: true
  - name: resume
    label: Upload Resume
    type: file
    required: false
    allowed_extensions:
    - .pdf
    - .docx
    max_size: 5
  recaptcha_site_key: ''
  description: We would love to hear from you!
---

# Contact Us

We would love to hear from you!

<!-- The actual form UI will be rendered by the 'form' layout/template -->
