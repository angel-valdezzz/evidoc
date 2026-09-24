Feature: Evidoc API execution capture
  The standalone API should create durable evidence artifacts and result files
  without depending on a test framework runtime.

  Scenario: Persist a successful test execution with a file attachment
    Given a clean Evidoc results directory
    And an attachment file named "input-data.txt"
    When a test named "Checkout flow" is captured through the Evidoc API
    And the step "Submit order" is logged with status "PASS"
    And an info message "Checkout submitted successfully" is logged
    And the attachment is added with description "Input payload"
    And the test ends with status "PASS" and duration 1.5
    Then a result file is generated for the captured test
    And the stored result declares status "PASS"
    And the stored result references one external file

  Scenario: Tolerate missing attachments without breaking the test result
    Given a clean Evidoc results directory
    When a test named "Missing evidence flow" is captured through the Evidoc API
    And a missing attachment path is added
    And the test ends with status "WARN" and duration 0.2
    Then a result file is generated for the captured test
    And the stored result declares status "WARN"
    And the warning log mentions a missing artifact
