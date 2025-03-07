package provider

import (
	"context"

	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/provider"
	"github.com/hashicorp/terraform-plugin-framework/resource"
)

var (
	_ provider.Provider = &lagoProvider{}
)

func New(version string) func() provider.Provider {
	return func() provider.Provider {
		return &lagoProvider{
			version: version,
		}
	}
}

type lagoProvider struct {
	version string
}

func (p *lagoProvider) Schema(ctx context.Context, req provider.SchemaRequest, resp *provider.SchemaResponse) {

}

func (p *lagoProvider) Configure(ctx context.Context, req provider.ConfigureRequest, resp *provider.ConfigureResponse) {

}

func (p *lagoProvider) Metadata(ctx context.Context, req provider.MetadataRequest, resp *provider.MetadataResponse) {
	resp.TypeName = "lago"
}

func (p *lagoProvider) DataSources(ctx context.Context) []func() datasource.DataSource {
	return []func() datasource.DataSource{}
}

func (p *lagoProvider) Resources(ctx context.Context) []func() resource.Resource {
	return []func() resource.Resource{}
}
