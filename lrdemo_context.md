# lrdemo Context

## Apps
### apps/__init__.py
### apps/notifications/apps.py
- Class: NotificationsConfig
### apps/notifications/admin.py
### apps/notifications/__init__.py
### apps/notifications/views/__init__.py
### apps/notifications/templates/__init__.py
### apps/notifications/services/notification_service.py
- Function: _clean_message
- Function: _build_broadcast_audit_description
- Function: create_vacation_status_notification
- Function: create_vacation_submission_notifications
- Function: create_broadcast_info_notifications
- Function: mark_user_notifications_as_read
### apps/notifications/services/__init__.py
### apps/notifications/selectors/__init__.py
### apps/notifications/models/notification.py
- Class: Notification
### apps/notifications/models/__init__.py
### apps/employees/apps.py
- Class: EmployeesConfig
### apps/employees/urls.py
### apps/employees/admin.py
- Class: DepartmentAdmin
- Class: EmployeeAdmin
### apps/employees/__init__.py
### apps/employees/forms.py
- Class: EmployeeOnboardingForm
### apps/employees/views/onboarding.py
- Function: onboarding_view
### apps/employees/views/__init__.py
### apps/employees/templates/__init__.py
### apps/employees/services/__init__.py
### apps/employees/selectors/__init__.py
### apps/employees/models/department.py
- Class: Department
### apps/employees/models/employee.py
- Class: Employee
### apps/employees/models/__init__.py
### apps/dashboard/views.py
- Function: _normalize_roles
- Function: _pick_role
- Function: _redirect_back
- Function: _can_access_rrhh_area
- Function: role_required
- Function: _build_employee_dashboard_context
- Function: home_view
- Function: employee_request_view
- Function: admin_panel_view
- Function: profile_view
- Function: rrhh_history_view
- Function: rrhh_export_requests_view
- Function: rrhh_export_download_view
- Function: notification_panel_view
- Function: notification_stream_view
- Function: mark_notifications_read_view
- Function: mark_notification_read_view
### apps/dashboard/apps.py
### apps/dashboard/urls.py
### apps/dashboard/live_updates.py
- Function: _build_live_update_key
- Function: bump_dashboard_live_revision
- Function: get_dashboard_live_revision
### apps/dashboard/selectors.py
- Function: _non_empty_query_string
- Function: _full_name
- Function: _format_preview_cell
- Function: _status_id_map
- Function: get_user_profile
- Function: get_display_name
- Function: build_role_context
- Function: apply_request_filters
- Function: get_employee_requests
- Function: get_rrhh_review_requests
- Function: build_rrhh_overlap_context
- Function: format_export_filters
- Function: get_rrhh_export_history_queryset
- Function: resolve_rrhh_export_file
- Function: build_rrhh_export_history
- Function: build_rrhh_export_preview
- Function: build_rrhh_page_context
- Function: build_admin_page_context
- Function: summarize_ids
- Function: get_admin_audit_queryset
- Function: build_admin_audit_summary
- Function: build_admin_audit_entries
- Function: notification_type_from_message
- Function: serialize_notification
- Function: build_notification_context
- Function: get_notification_state
- Function: get_dashboard_live_state
- Function: get_admin_user_listing
- Function: get_admin_audit_options
### apps/dashboard/__init__.py
### apps/dashboard/forms.py
- Class: AdminUserCreateForm
- Class: AdminBulkActionForm
- Class: AdminUserUpdateForm
- Class: AdminUserPasswordForm
- Class: AdminRoleCreateForm
- Class: AdminDepartmentCreateForm
- Class: AdminNotificationBroadcastForm
- Class: EmployeeProfileUpdateForm
### apps/dashboard/services/admin_actions.py
- Function: _clean_text
- Function: _clean_optional_text
- Function: _resolve_role_label
- Function: _summarize_ids
- Function: toggle_user_active
- Function: create_user_from_admin
- Function: apply_bulk_action
- Function: create_role_from_admin
- Function: create_department_from_admin
- Function: update_user_from_admin
- Function: set_user_password_from_admin
### apps/dashboard/services/__init__.py
### apps/vacations/apps.py
- Class: VacationsConfig
### apps/vacations/urls.py
### apps/vacations/admin.py
### apps/vacations/__init__.py
### apps/vacations/forms.py
- Class: VacationRequestForm
- Class: VacationReviewForm
### apps/vacations/views/__init__.py
### apps/vacations/views/requests.py
- Function: _redirect_back
- Function: request_vacation_view
- Function: review_vacation_request_view
### apps/vacations/templates/__init__.py
### apps/vacations/services/statuses.py
- Function: _build_name_query
- Function: get_status_ids
- Function: get_status
### apps/vacations/services/balance.py
- Function: _days_inclusive
- Function: _truncate_days
- Function: split_range_by_year
- Function: overlap_days_for_year
- Function: get_total_requested_days
- Function: _get_employee_year_requests
- Function: merge_continuous_ranges
- Function: build_employee_vacation_blocks
- Function: block_has_days_outside_peak_months
- Function: get_year_entitlement
- Function: get_employee_yearly_balance
- Function: is_preferred_period
- Function: requires_planning_notice
- Function: sync_employee_counters
### apps/vacations/services/notifications.py
- Function: get_rrhh_recipient_emails
- Function: send_vacation_request_notification
### apps/vacations/services/export.py
- Function: _resolved_export_headers
- Function: _style_export_sheet
- Function: get_vacation_exports_directory
- Function: build_rrhh_export_filename
- Function: save_vacation_export_file
- Function: build_vacation_request_workbook
- Function: build_vacation_requests_workbook
### apps/vacations/services/workflow.py
- Function: _validate_request_natural_year
- Function: _find_overlapping_request
- Function: validate_request_overlap
- Function: validate_request_blocks
- Function: validate_request_submission
- Function: validate_request_balance
- Function: validate_request_approval
- Function: create_vacation_request
- Function: deliver_request_export
- Function: review_vacation_request
### apps/vacations/services/summary.py
- Function: get_employee_dashboard_summary
### apps/vacations/services/__init__.py
### apps/vacations/selectors/__init__.py
### apps/vacations/models/vacation_status.py
- Class: VacationStatus
### apps/vacations/models/vacation_request.py
- Class: VacationRequest
### apps/vacations/models/vacation_request_history.py
- Class: VacationRequestHistory
### apps/vacations/models/__init__.py
### apps/audit/apps.py
- Class: AuditConfig
### apps/audit/admin.py
### apps/audit/__init__.py
### apps/audit/views/__init__.py
### apps/audit/templates/__init__.py
### apps/audit/services/audit_service.py
- Function: get_audit_action_label
- Function: get_audit_resource_label
- Function: log_audit_event
### apps/audit/services/__init__.py
### apps/audit/selectors/__init__.py
### apps/audit/models/audit_log.py
- Class: AuditLog
### apps/audit/models/export_history.py
- Class: ExportHistory
### apps/audit/models/__init__.py
### apps/users/apps.py
- Class: UsersConfig
### apps/users/urls.py
### apps/users/admin.py
- Class: UserRoleInline
- Class: EmployeeInline
- Class: UserAdmin
- Class: RoleAdmin
- Class: UserRoleAdmin
### apps/users/validators.py
- Function: normalize_dni
- Function: validate_dni
### apps/users/backends.py
- Class: DNIBackend
### apps/users/admin_forms.py
- Class: AdminUserCreationForm
- Class: AdminUserChangeForm
### apps/users/__init__.py
### apps/users/forms.py
- Class: RequestActivationForm
- Class: SetPasswordForm
- Class: LoginForm
### apps/users/management/__init__.py
### apps/users/management/commands/seed_roles.py
- Class: Command
### apps/users/management/commands/__init__.py
### apps/users/views/auth_views.py
- Function: _client_ip
- Function: _rate_limit_response
- Function: anonymous_required
- Function: _toast_response
- Function: request_activation_view
- Function: set_password_view
- Function: login_view
- Function: logout_view
### apps/users/views/__init__.py
### apps/users/templates/__init__.py
### apps/users/services/email_service.py
- Function: get_email_provider
- Function: build_activation_email_message
- Function: _normalize_resend_attachment
- Function: _send_via_django_backend
- Function: _send_via_resend
- Function: send_email_message
- Function: send_activation_email
### apps/users/services/auth_service.py
- Function: request_activation
- Function: validate_token
- Function: set_password
### apps/users/services/__init__.py
### apps/users/selectors/__init__.py
### apps/users/models/user.py
- Class: UserManager
- Class: User
- Class: UserRole
### apps/users/models/role.py
- Class: Role
### apps/users/models/__init__.py
### apps/core/views.py
- Function: health_view
### apps/core/apps.py
- Class: CoreConfig
### apps/core/logging.py
- Class: EnvironmentFilter
### apps/core/http.py
- Function: get_client_ip
- Function: is_htmx_request
### apps/core/permissions.py
- Function: normalize_roles
- Function: has_role
- Function: pick_role
- Function: get_primary_role
- Function: role_required
### apps/core/i18n.py
- Function: _normalize_value
- Function: translate_text
- Function: get_role_label
- Function: get_status_label
- Function: get_review_status_label
- Function: get_export_status_label
### apps/core/rate_limits.py
- Function: _normalize_identifier
- Function: build_rate_limit_key
- Function: is_rate_limited
- Function: register_rate_limit_attempt
- Function: reset_rate_limit
### apps/core/admin.py
### apps/core/middleware.py
- Class: OnboardingRequiredMiddleware
### apps/core/__init__.py
### apps/core/templatetags/i18n_extras.py
### apps/core/templatetags/__init__.py
### apps/core/models/base.py
- Class: CreatedAtModel
- Class: TimeStampedModel
### apps/core/models/__init__.py

## Templates
- templates/base.html
- templates/components/modal.html
- templates/components/button.html
- templates/components/toast_card.html
- templates/components/inputs/text_input.html
- templates/components/inputs/select_input.html
- templates/components/inputs/date_input.html
- templates/layouts/dashboard_base.html
- .venv/lib/python3.12/site-packages/django/views/templates/csrf_403.html
- .venv/lib/python3.12/site-packages/django/views/templates/technical_500.html
- .venv/lib/python3.12/site-packages/django/views/templates/default_urlconf.html
- .venv/lib/python3.12/site-packages/django/views/templates/technical_404.html
- .venv/lib/python3.12/site-packages/django/views/templates/directory_index.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/table.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/attrs.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/label.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/field.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/div.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/ul.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/p.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/formsets/table.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/formsets/div.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/formsets/ul.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/formsets/p.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/errors/list/ul.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/errors/list/default.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/errors/dict/ul.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/errors/dict/default.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/select_date.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/file.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/radio.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/number.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/splitdatetime.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/tel.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/color.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/time.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/multiple_hidden.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/radio_option.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/textarea.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/select_option.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/input.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/clearable_file_input.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/multiple_input.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/checkbox_option.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/attrs.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/search.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/input_option.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/checkbox_select.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/datetime.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/password.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/checkbox.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/url.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/multiwidget.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/hidden.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/text.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/date.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/splithiddendatetime.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/select.html
- .venv/lib/python3.12/site-packages/django/forms/templates/django/forms/widgets/email.html
- .venv/lib/python3.12/site-packages/django/contrib/gis/templates/gis/openlayers.html
- .venv/lib/python3.12/site-packages/django/contrib/admindocs/templates/admin_doc/bookmarklets.html
- .venv/lib/python3.12/site-packages/django/contrib/admindocs/templates/admin_doc/view_detail.html
- .venv/lib/python3.12/site-packages/django/contrib/admindocs/templates/admin_doc/template_tag_index.html
- .venv/lib/python3.12/site-packages/django/contrib/admindocs/templates/admin_doc/view_index.html
- .venv/lib/python3.12/site-packages/django/contrib/admindocs/templates/admin_doc/model_detail.html
- .venv/lib/python3.12/site-packages/django/contrib/admindocs/templates/admin_doc/template_detail.html
- .venv/lib/python3.12/site-packages/django/contrib/admindocs/templates/admin_doc/missing_docutils.html
- .venv/lib/python3.12/site-packages/django/contrib/admindocs/templates/admin_doc/index.html
- .venv/lib/python3.12/site-packages/django/contrib/admindocs/templates/admin_doc/template_filter_index.html
- .venv/lib/python3.12/site-packages/django/contrib/admindocs/templates/admin_doc/model_index.html
- .venv/lib/python3.12/site-packages/django/contrib/postgres/templates/postgres/widgets/split_array.html
- .venv/lib/python3.12/site-packages/django/contrib/auth/templates/auth/widgets/read_only_password_hash.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/registration/logged_out.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/registration/password_reset_complete.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/registration/password_reset_email.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/registration/password_reset_form.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/registration/password_reset_confirm.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/registration/password_change_form.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/registration/password_reset_done.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/registration/password_change_done.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/base.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/submit_line.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/500.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/color_theme_toggle.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/delete_selected_confirmation.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/pagination.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/delete_confirmation.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/change_form.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/actions.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/login.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/search_form.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/invalid_setup.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/404.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/change_list.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/prepopulated_fields_js.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/change_list_results.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/date_hierarchy.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/object_history.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/app_index.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/base_site.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/change_list_object_tools.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/change_form_object_tools.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/nav_sidebar.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/index.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/filter.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/app_list.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/popup_response.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/includes/object_delete_summary.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/includes/fieldset.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/edit_inline/stacked.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/edit_inline/tabular.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/auth/user/add_form.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/auth/user/change_password.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/widgets/radio.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/widgets/time.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/widgets/clearable_file_input.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/widgets/foreign_key_raw_id.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/widgets/many_to_many_raw_id.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/widgets/split_datetime.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/widgets/url.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/widgets/related_widget_wrapper.html
- .venv/lib/python3.12/site-packages/django/contrib/admin/templates/admin/widgets/date.html
- apps/employees/templates/employees/onboarding.html
- apps/dashboard/templates/dashboard/employee_request.html
- apps/dashboard/templates/dashboard/admin_panel.html
- apps/dashboard/templates/dashboard/no_role.html
- apps/dashboard/templates/dashboard/home.html
- apps/dashboard/templates/dashboard/employee.html
- apps/dashboard/templates/dashboard/admin.html
- apps/dashboard/templates/dashboard/rrhh_history.html
- apps/dashboard/templates/dashboard/rrhh.html
- apps/dashboard/templates/dashboard/profile.html
- apps/dashboard/templates/dashboard/partials/notification_shell.html
- apps/dashboard/templates/dashboard/partials/admin_notification_form.html
- apps/dashboard/templates/dashboard/partials/notification_panel.html
- apps/dashboard/templates/dashboard/partials/admin_department_form.html
- apps/dashboard/templates/dashboard/partials/admin_edit_user_form.html
- apps/dashboard/templates/dashboard/partials/admin_role_form.html
- apps/dashboard/templates/dashboard/partials/admin_password_form.html
- apps/dashboard/templates/dashboard/partials/admin_create_user_form.html
- apps/users/templates/users/invalid_token.html
- apps/users/templates/users/login.html
- apps/users/templates/users/set_password.html
- apps/users/templates/users/request_activation.html
