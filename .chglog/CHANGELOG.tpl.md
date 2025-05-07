# Changelog

{{ range .Versions }}
<a name="{{ .Tag.Name }}"></a>
## {{ if .Tag.Previous }}[{{ .Tag.Name }}]({{ $.Info.RepositoryURL }}/compare/{{ .Tag.Previous.Name }}...{{ .Tag.Name }}){{ else }}{{ .Tag.Name }}{{ end }} ({{ datetime "2006-01-02" .Tag.Date }})

{{ if .CommitGroups }}
### Changes
{{ range .CommitGroups }}
#### {{ .Title }}
{{ range .Commits }}
- {{ .Subject }}
{{ end }}
{{ end }}
{{ end }}

{{ if .RevertCommits }}
### Reverted Changes
{{ range .RevertCommits }}
- {{ .Revert.Header }}
{{ end }}
{{ end }}

{{ if .MergeCommits }}
### Merged Pull Requests
{{ range .MergeCommits }}
- {{ .Header }}
{{ end }}
{{ end }}

{{ if .NoteGroups }}
### Release Notes
{{ range .NoteGroups }}
#### {{ .Title }}
{{ range .Notes }}
- {{ .Body }}
{{ end }}
{{ end }}
{{ end }}

---
{{ end }}