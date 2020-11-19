SELECT notes.`data` FROM notes,users,associations
WHERE users.id = associations.user
AND associations.note = notes.id
AND users.id = %s