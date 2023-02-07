! Description:
! Solver job input file reader.
module m_reader
    use data_model
    implicit none
    
    private
    public read_input
    
    ! error messages
    character(*), parameter :: ERROR_UNDEFINED_INPUT_SEQUENCE = 'Error: undefined input sequence'
    
    contains
    
    ! Description:
    ! Create a new finite element model database by reading the user-specified job input file.
    type(t_mdb) function read_input(file) result(mdb)
        character(*), intent(in) :: file ! solver job input file path
        
        ! reader helper variables
        character(64) :: command                      ! current command being parsed
        character(4)  :: version                      ! job input file version
        character(3)  :: advance                      ! reader advance flag
        integer       :: i, j                         ! loop counters
        integer       :: ip1, ip2, ip3, ip4, ip5, ip6 ! integer parameters
        real          :: rp1, rp2, rp3                ! real parameters
        logical       :: lp1, lp2, lp3                ! logical parameters
        type(t_mesh)  :: mesh                         ! finite element mesh
        
        ! open solver job input file for reading
        open(unit=1, action='read', file=file)
        
        ! parse: mesh
        read(unit=1, fmt=*) command; if (trim(command) /= 'mesh') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
        read(unit=1, fmt=*) ip1, ip2, ip3; mesh = new_mesh(ip1, ip2, ip3)
        
        ! parse: nodes
        read(unit=1, fmt=*) command; if (trim(command) /= 'nodes') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
        do i = 1, mesh%n_nodes
            read(unit=1, fmt=*) rp1, rp2, rp3; mesh%nodes(i) = new_node(mesh%m_space, rp1, rp2, rp3)
        end do
        
        ! parse: elements
        read(unit=1, fmt=*) command; if (trim(command) /= 'elements') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
        do i = 1, mesh%n_elements
            read(unit=1, fmt='(I,I)', advance='no') ip1, ip2; mesh%elements(i) = new_element(ip1, ip2)
            advance = 'no'
            do j = 1, mesh%elements(i)%n_nodes
                if (j == mesh%elements(i)%n_nodes) advance = 'yes'
                read(unit=1, fmt='(I)', advance=advance) mesh%elements(i)%i_nodes(j)
            end do
        end do
        
        ! parse: database
        read(unit=1, fmt=*) command; if (trim(command) /= 'database') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
        read(unit=1, fmt=*) ip1, ip2, ip3, ip4, ip5, ip6; mdb = new_mdb(ip1, ip2, ip3, ip4, ip5, ip6, mesh)
        
        ! parse: node-set
        do i = 1, mdb%n_nsets
            read(unit=1, fmt=*) command; if (trim(command) /= 'node-set') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1; mdb%nsets(i) = new_nset(ip1)
            do j = 1, mdb%nsets(i)%n_nodes
                read(unit=1, fmt=*) mdb%nsets(i)%i_nodes(j)
            end do
        end do
        
        ! parse: element-set
        do i = 1, mdb%n_esets
            read(unit=1, fmt=*) command; if (trim(command) /= 'element-set') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1; mdb%esets(i) = new_eset(ip1)
            do j = 1, mdb%esets(i)%n_elements
                read(unit=1, fmt=*) mdb%esets(i)%i_elements(j)
            end do
        end do
        
        ! parse: material
        do i = 1, mdb%n_materials
            read(unit=1, fmt=*) command; if (trim(command) /= 'material') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) rp1, rp2, rp3; mdb%materials(i) = new_material(rp1, rp2, rp3)
        end do
        
        ! parse: section
        do i = 1, mdb%n_sections
            read(unit=1, fmt=*) command; if (trim(command) /= 'section') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1, ip2, ip3, rp1; mdb%sections(i) = new_section(mdb%mesh%m_space, ip1, ip2, ip3, rp1)
        end do
        
        ! parse: concentrated-load
        do i = 1, mdb%n_cloads
            read(unit=1, fmt=*) command; if (trim(command) /= 'concentrated-load') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1, rp1, rp2, rp3; mdb%cloads(i) = new_cload(ip1, rp1, rp2, rp3)
        end do
        
        ! parse: boundary-condition
        do i = 1, mdb%n_boundaries
            read(unit=1, fmt=*) command; if (trim(command) /= 'boundary-condition') error stop ERROR_UNDEFINED_INPUT_SEQUENCE
            read(unit=1, fmt=*) ip1, rp1, rp2, rp3, lp1, lp2, lp3; mdb%boundaries(i) = new_boundary(ip1, rp1, rp2, rp3, lp1, lp2, lp3)
        end do
        
        ! final actions
        call mdb%mesh%count_elements_per_node()
        
        ! close file
        close(unit=1)
    end function
    
end module
