from rest_framework import serializers

from site_module.models import SiteSetting


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = ['id', 'author', 'site_name', 'site_url', 'office_address',
                  'office_phone', 'backup_phone', 'fax', 'email', 'copy_right_text',
                  'about_us_text', 'founder', 'site_logo', 'E_namad_code', 'instagram_link',
                  'linkedin_link', 'facebook_link', 'is_main_setting', 'created_date']

    # def validate(self, attrs):
    #     # Example validation logic
    #     if not attrs.get('site_name'):
    #         raise serializers.ValidationError({
    #             "success": False,
    #             "data": {},
    #             "message": "Site name is required."
    #         })
    #     return attrs
