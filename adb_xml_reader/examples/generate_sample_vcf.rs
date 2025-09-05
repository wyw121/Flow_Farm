use adb_xml_reader::vcf_import::VcfImporter;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    println!("🎯 生成示例VCF文件...");

    VcfImporter::generate_sample_vcf()?;

    // 同时读取并显示VCF文件内容
    let vcf_content = std::fs::read_to_string("sample_contact.vcf")?;
    println!("\n📄 生成的VCF文件内容:");
    println!("{}", "=".repeat(50));
    println!("{}", vcf_content);
    println!("{}", "=".repeat(50));

    Ok(())
}
