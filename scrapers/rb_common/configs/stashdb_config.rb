# frozen_string_literal: true

require_relative "config_base"

module Config
  class StashDB < ConfigBase
    # Tweak user settings below. An API Key can be generated in StashDB's user page
    USER_CONFIG = {
      endpoint: "https://stashdb.org/graphql",
      api_key: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJ5aW56YnVyZ2hiZWFyIiwic3ViIjoiQVBJS2V5IiwiaWF0IjoxNzI4MjY4OTYxfQ.WJdwO1Yg8g3VMqCXEtBHMISjb73uJ-JXE3L2mtUij4s"
    }
  end
end
